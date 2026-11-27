
"""Async UDP task broker for trusted localhost only."""

import asyncio
import base64
import json
import logging
import time
import uuid
from collections import OrderedDict, deque

import cloudpickle

from meshweaver.metrics import TaskMetrics
from meshweaver.task_state import TaskRegistry, TaskState


MAX_PACKET = 60000

logger = logging.getLogger("meshweaver.broker")


def encode(message):
    payload = json.dumps(
        message, separators=(",", ":")
    ).encode("utf-8")

    if len(payload) > MAX_PACKET:
        raise ValueError("UDP message exceeds 60000-byte demo limit")

    return payload


def decode(payload):
    if len(payload) > MAX_PACKET:
        raise ValueError("Oversized packet")

    message = json.loads(payload.decode("utf-8"))

    if not isinstance(message, dict):
        raise ValueError("Expected JSON object")

    return message


class Worker(asyncio.DatagramProtocol):

    def __init__(self, max_concurrent=2, max_queue=100):
        if not isinstance(max_concurrent, int) or max_concurrent < 1:
            raise ValueError('max_concurrent must be a positive integer')
        if not isinstance(max_queue, int) or max_queue < 0:
            raise ValueError('max_queue must be a non-negative integer')
        self.max_concurrent = max_concurrent
        self.max_queue = max_queue
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.waiting = deque()
        self.running = 0
        self.max_running_observed = 0
        self.rejected_count = 0
        self.transport = None
        self.completed = OrderedDict()
        self.tasks = set()
        self.in_flight = set()
        self.duplicate_count = 0
        self.task_map = {}
        self.sync_running = set()
        self.cancelled_count = 0
        self.cancelled_owners = OrderedDict()
        self.cancel_handlers = set()
        self.shutting_down = False
        self.registry = TaskRegistry()

    def connection_made(self, transport):
        self.transport = transport
        logger.info("Worker connected and ready")

    def datagram_received(self, data, addr):
        if addr[0] != "127.0.0.1":
            return

        try:
            msg = decode(data)

            if msg.get("type") == "status_query":
                task_id = msg.get("id")
                request_id = msg.get("request_id")

                if (
                    not isinstance(task_id, str)
                    or not 0 < len(task_id) <= 64
                    or not isinstance(request_id, str)
                    or not 0 < len(request_id) <= 64
                ):
                    raise ValueError("Invalid status query")

                self._handle_status_query(
                    task_id, request_id, addr
                )
                return

            if msg.get("type") == "cancel":
                task_id = msg.get("id")
                request_id = msg.get("request_id")

                if (
                    not isinstance(task_id, str)
                    or not 0 < len(task_id) <= 64
                    or not isinstance(request_id, str)
                    or not 0 < len(request_id) <= 64
                ):
                    raise ValueError("Invalid cancellation message")

                handler = asyncio.create_task(
                    self._handle_cancel(task_id, request_id, addr)
                )
                self.cancel_handlers.add(handler)
                handler.add_done_callback(
                    self.cancel_handlers.discard
                )
                return

            if msg.get("type") == "ping":
                ping_id = msg.get("id")

                if (
                    not isinstance(ping_id, str)
                    or not 0 < len(ping_id) <= 64
                ):
                    raise ValueError("Invalid ping id")

                self.transport.sendto(
                    encode({
                        "type": "pong",
                        "id": ping_id,
                    }),
                    addr,
                )

                logger.info(
                    "Worker heartbeat responded | ping_id=%s",
                    ping_id,
                )
                return

            if (
                msg.get("type") != "task"
                or not isinstance(msg.get("id"), str)
            ):
                raise ValueError("Invalid task message")

            task_id = msg["id"]

            if not 0 < len(task_id) <= 64:
                raise ValueError("Invalid task id")

            if task_id in self.completed:
                self.duplicate_count += 1
                logger.info(
                    "Cached result returned | task_id=%s",
                    task_id,
                )

                self.transport.sendto(
                    self.completed[task_id],
                    addr,
                )
                return

            if task_id in self.in_flight:
                self.duplicate_count += 1
                logger.info(
                    "Duplicate task suppressed | task_id=%s",
                    task_id,
                )
                self.transport.sendto(
                    encode({"type": "ack", "id": task_id}), addr
                )
                return

            if self.shutting_down:
                self.transport.sendto(encode({
                    "type": "result",
                    "id": task_id,
                    "ok": False,
                    "error": "Worker is shutting down",
                }), addr)
                return

            if self.running + len(self.waiting) >= (
                self.max_concurrent + self.max_queue
            ):
                self.rejected_count += 1
                self.transport.sendto(encode({
                    "type": "result",
                    "id": task_id,
                    "ok": False,
                    "error": "Worker queue is full",
                }), addr)
                return

            logger.info(
                "Task received | task_id=%s",
                task_id,
            )

            self.transport.sendto(
                encode({
                    "type": "ack",
                    "id": task_id,
                }),
                addr,
            )

            self.registry.create(task_id, owner=addr)
            self.registry.transition(task_id, TaskState.QUEUED)
            self.waiting.append(task_id)
            task = asyncio.create_task(
                self.execute(msg, addr)
            )

            self.in_flight.add(task_id)
            self.tasks.add(task)
            self.task_map[task_id] = (task, addr)
            task.add_done_callback(
                lambda finished: self._task_done(task_id, finished)
            )

        except (
            ValueError,
            UnicodeError,
            KeyError,
            TypeError,
        ) as exc:
            logger.warning(
                "Invalid message rejected | error=%s",
                type(exc).__name__,
            )

    def _task_done(self, task_id, task):
        entry = self.task_map.get(task_id)

        if task.cancelled() and entry is not None:
            _, addr = entry

            packet = encode({
                "type": "result",
                "id": task_id,
                "ok": False,
                "error": "Task cancelled",
                "cancelled": True,
            })

            self.completed[task_id] = packet
            self.cancelled_owners[task_id] = addr
            self.cancelled_count += 1
            self.registry.transition(
                task_id, TaskState.CANCELLED, 'Task cancelled'
            )

            if len(self.completed) > 256:
                self.completed.popitem(last=False)

            if len(self.cancelled_owners) > 256:
                self.cancelled_owners.popitem(last=False)

            self.transport.sendto(packet, addr)

            logger.info(
                "Task cancelled | task_id=%s", task_id
            )

        self.tasks.discard(task)
        self.task_map.pop(task_id, None)
        self.in_flight.discard(task_id)

        if task_id in self.waiting:
            self.waiting.remove(task_id)

    async def cancel_task(self, task_id):
        """Cancel a queued or running asynchronous task."""
        entry = self.task_map.get(task_id)

        if entry is None:
            return False

        task, addr = entry

        if task.done() or task_id in self.sync_running:
            return False

        if task.cancelling():
            return False

        task.cancel()

        await asyncio.gather(
            task, return_exceptions=True
        )

        return task.cancelled()

    async def _handle_cancel(self, task_id, request_id, addr):
        """Process a cancellation request from the task owner."""
        entry = self.task_map.get(task_id)
        cancelled = False
        reason = "Task not found or already completed"

        if (
            task_id in self.completed
            and self.cancelled_owners.get(task_id) == addr
            and decode(self.completed[task_id]).get("error")
                == "Task cancelled"
        ):
            cancelled = True
            reason = "Task cancelled"

        elif entry is not None:
            task, owner = entry

            if owner != addr:
                reason = "Cancellation not authorized"

            elif task_id in self.sync_running:
                reason = "Running synchronous task cannot be cancelled"

            elif task.cancelling():
                await asyncio.gather(
                    task, return_exceptions=True
                )
                cancelled = task.cancelled()
                reason = (
                    "Task cancelled" if cancelled
                    else "Task cancellation rejected"
                )

            else:
                cancelled = await self.cancel_task(task_id)
                reason = (
                    "Task cancelled" if cancelled
                    else "Task cancellation rejected"
                )

        response = encode({
            "type": "cancel_ack",
            "id": task_id,
            "request_id": request_id,
            "ok": cancelled,
            "reason": reason,
        })

        self.transport.sendto(response, addr)

        logger.info(
            "Cancellation response | task_id=%s | success=%s",
            task_id, cancelled,
        )

    async def shutdown(self, cancel_pending=False):
        """Stop accepting new tasks and finish existing work."""
        self.shutting_down = True

        logger.info("Worker shutdown started")

        if cancel_pending:
            await asyncio.gather(
                *(
                    self.cancel_task(task_id)
                    for task_id in list(self.task_map)
                ),
                return_exceptions=True,
            )

        if self.tasks:
            await asyncio.gather(
                *list(self.tasks),
                return_exceptions=True,
            )

        if self.cancel_handlers:
            await asyncio.gather(
                *list(self.cancel_handlers),
                return_exceptions=True,
            )

        if self.transport is not None:
            self.transport.close()

        logger.info("Worker shutdown completed")

    def _handle_status_query(
        self, task_id, request_id, addr
    ):
        """Return task status only to the registered owner."""

        record = self.registry.get(task_id)
        owner = self.registry.get_owner(task_id)

        allowed = record is not None and owner == addr

        response = {
            "type": "status_response",
            "id": task_id,
            "request_id": request_id,
            "ok": allowed,
        }

        if allowed:
            response["status"] = record
        else:
            response["error"] = "Task status unavailable"

        self.transport.sendto(
            encode(response), addr
        )

        logger.info(
            "Status query processed | task_id=%s | success=%s",
            task_id, allowed,
        )

    def get_task_status(self, task_id):
        """Return a copy of the worker task record."""
        return self.registry.get(task_id)

    def get_task_state_counts(self):
        return self.registry.snapshot()

    def get_queue_stats(self):
        """Return worker queue and concurrency statistics."""
        return {
            "waiting": len(self.waiting),
            "running": self.running,
            "max_concurrent": self.max_concurrent,
            "max_queue": self.max_queue,
            "max_running_observed": self.max_running_observed,
            "rejected": self.rejected_count,
            "duplicates": self.duplicate_count,
            "cancelled": self.cancelled_count,
            "shutting_down": self.shutting_down,
        }

    async def execute(self, msg, addr):
        task_id = msg["id"]
        try:
            async with self.semaphore:
                self.waiting.remove(task_id)
                self.running += 1
                self.registry.transition(task_id, TaskState.RUNNING)
                self.max_running_observed = max(
                    self.max_running_observed, self.running
                )
                try:
                    await self._execute_task(msg, addr)
                finally:
                    self.running -= 1
        finally:
            if task_id in self.waiting:
                self.waiting.remove(task_id)
            # The done callback owns final tracking cleanup.

    async def _execute_task(self, msg, addr):
        task_id = msg["id"]
        start_time = time.perf_counter()

        logger.info(
            "Task execution started | task_id=%s",
            task_id,
        )

        try:
            raw = base64.b64decode(
                msg["payload"],
                validate=True,
            )

            if len(raw) > 45000:
                raise ValueError("Task payload too large")

            function, args, kwargs = cloudpickle.loads(raw)

            if (
                not callable(function)
                or not isinstance(args, tuple)
                or not isinstance(kwargs, dict)
            ):
                raise ValueError("Invalid function arguments")

            if asyncio.iscoroutinefunction(function):
                result = await function(*args, **kwargs)

            else:
                self.sync_running.add(task_id)
                try:
                    result = await asyncio.to_thread(
                        function, *args, **kwargs
                    )
                finally:
                    self.sync_running.discard(task_id)

            packet = encode({
                "type": "result",
                "id": task_id,
                "ok": True,
                "value": result,
            })

            logger.info(
                "Task completed | task_id=%s | duration=%.3fs",
                task_id,
                time.perf_counter() - start_time,
            )

        except Exception as exc:
            packet = encode({
                "type": "result",
                "id": task_id,
                "ok": False,
                "error": (
                    f"{type(exc).__name__}: "
                    f"{str(exc)[:200]}"
                ),
            })

            logger.error(
                "Task failed | task_id=%s | error=%s | duration=%.3fs",
                task_id,
                type(exc).__name__,
                time.perf_counter() - start_time,
            )

        outcome = decode(packet)
        self.registry.transition(
            task_id,
            TaskState.COMPLETED if outcome['ok'] else TaskState.FAILED,
            outcome.get('error'),
        )
        self.completed[task_id] = packet
        self.in_flight.discard(task_id)

        if len(self.completed) > 256:
            self.completed.popitem(last=False)

        self.transport.sendto(packet, addr)

    def connection_lost(self, exc):
        logger.info("Worker connection closed")


class Client(asyncio.DatagramProtocol):

    def __init__(self):
        self.transport = None
        self.pending = {}
        self.health_pending = {}
        self.cancel_pending = {}
        self.status_pending = {}

        # Task execution metrics
        self.metrics = TaskMetrics()

    def connection_made(self, transport):
        self.transport = transport
        logger.info("Client connected to worker")

    def datagram_received(self, data, addr):
        if addr[0] != "127.0.0.1":
            return

        try:
            msg = decode(data)
            msg_type = msg.get("type")
            msg_id = msg.get("id")

            if msg_type == "status_response":
                request_id = msg.get("request_id")

                if not isinstance(request_id, str):
                    return

                entry = self.status_pending.get(request_id)

                if entry is not None:
                    task_id, future = entry
                    ok = msg.get("ok")
                    record = msg.get("status")

                    valid = (
                        isinstance(ok, bool)
                        and (
                            not ok
                            or (
                                isinstance(record, dict)
                                and record.get("task_id") == task_id
                                and record.get("state") in {
                                    state.value for state in TaskState
                                }
                            )
                        )
                    )

                    if (
                        msg_id == task_id
                        and valid
                        and not future.done()
                    ):
                        future.set_result(msg)

                return

            if msg_type == "cancel_ack":
                request_id = msg.get("request_id")
                entry = self.cancel_pending.get(request_id)

                if entry is not None:
                    task_id, future = entry

                    if (
                        msg_id == task_id
                        and isinstance(msg.get("ok"), bool)
                        and not future.done()
                    ):
                        future.set_result(msg)

                return

            if msg_type == "pong":
                future = self.health_pending.get(msg_id)

                if future is not None and not future.done():
                    future.set_result(msg)

                return

            if msg_type != "result":
                return

            future = self.pending.get(msg_id)

            if future is not None and not future.done():
                logger.info(
                    "Task response received | task_id=%s",
                    msg_id,
                )
                future.set_result(msg)

        except (
            ValueError,
            UnicodeError,
            TypeError,
        ) as exc:
            logger.warning(
                "Invalid response rejected | error=%s",
                type(exc).__name__,
            )

    def get_active_task_ids(self):
        """Return IDs of locally pending submissions."""
        return [
            task_id
            for task_id, future in self.pending.items()
            if not future.done()
        ]

    async def cancel_task(self, task_id, timeout=1.0, retries=2):
        """Request cancellation through the UDP protocol."""
        if not isinstance(task_id, str) or not 0 < len(task_id) <= 64:
            raise ValueError("Invalid task id")

        if timeout <= 0:
            raise ValueError("timeout must be positive")

        if not isinstance(retries, int) or retries < 0:
            raise ValueError("retries must be a non-negative integer")

        self.metrics.cancellation_requests += 1
        request_id = uuid.uuid4().hex
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        self.cancel_pending[request_id] = (task_id, future)

        packet = encode({
            "type": "cancel",
            "id": task_id,
            "request_id": request_id,
        })

        try:
            for attempt in range(retries + 1):
                self.transport.sendto(packet)

                try:
                    response = await asyncio.wait_for(
                        asyncio.shield(future),
                        timeout,
                    )

                    if response["ok"]:
                        self.metrics.cancellation_accepted += 1
                    else:
                        self.metrics.cancellation_rejected += 1
                    return response["ok"]

                except asyncio.TimeoutError:
                    self.metrics.cancellation_timeouts += 1
                    if attempt < retries:
                        self.metrics.cancellation_retries += 1
                    if attempt == retries:
                        raise TimeoutError(
                            "Cancellation response timed out"
                        ) from None

        finally:
            self.cancel_pending.pop(request_id, None)

            if not future.done():
                future.cancel()

    async def query_task_status(
        self, task_id, timeout=1.0, retries=2
    ):
        """Retrieve a task record through the UDP protocol."""

        if not isinstance(task_id, str) or not 0 < len(task_id) <= 64:
            raise ValueError("Invalid task id")

        if timeout <= 0:
            raise ValueError("timeout must be positive")

        if not isinstance(retries, int) or retries < 0:
            raise ValueError("Invalid retry count")

        request_id = uuid.uuid4().hex
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        packet = encode({
            "type": "status_query",
            "id": task_id,
            "request_id": request_id,
        })

        self.status_pending[request_id] = (
            task_id, future
        )

        try:
            for attempt in range(retries + 1):
                self.transport.sendto(packet)

                try:
                    response = await asyncio.wait_for(
                        asyncio.shield(future),
                        timeout,
                    )

                    if response["ok"]:
                        return response["status"]

                    return None

                except asyncio.TimeoutError:
                    if attempt == retries:
                        raise TimeoutError(
                            "Task status query timed out"
                        ) from None

                    logger.warning(
                        "Retrying status query | task_id=%s",
                        task_id,
                    )

        finally:
            self.status_pending.pop(request_id, None)

            if not future.done():
                future.cancel()

    def get_metrics(self):
        """Return current task execution statistics."""
        return self.metrics.snapshot()

    async def check_health(self, timeout=1.0):
        if timeout <= 0:
            raise ValueError("timeout must be positive")

        ping_id = uuid.uuid4().hex

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        self.health_pending[ping_id] = future

        try:
            logger.info(
                "Worker health check started | ping_id=%s",
                ping_id,
            )

            self.transport.sendto(
                encode({
                    "type": "ping",
                    "id": ping_id,
                })
            )

            try:
                response = await asyncio.wait_for(
                    future, timeout
                )

            except asyncio.TimeoutError:
                logger.warning(
                    "Worker health check timed out | ping_id=%s",
                    ping_id,
                )
                return False

            healthy = (
                response.get("type") == "pong"
                and response.get("id") == ping_id
            )

            logger.info(
                "Worker health check result | healthy=%s",
                healthy,
            )

            return healthy

        finally:
            self.health_pending.pop(ping_id, None)

    async def submit(
        self,
        function,
        *args,
        timeout=2.0,
        retries=2,
        **kwargs,
    ):
        if timeout <= 0:
            raise ValueError("timeout must be positive")

        if not isinstance(retries, int) or retries < 0:
            raise ValueError("retries must be a non-negative integer")

        task_id = uuid.uuid4().hex
        start_time = time.perf_counter()

        self.metrics.record_submission()

        remotely_cancelled = False
        future = None

        logger.info(
            "Task submitted | task_id=%s",
            task_id,
        )

        try:
            serialized = cloudpickle.dumps(
                (function, args, kwargs)
            )

            packet = encode({
                "type": "task",
                "id": task_id,
                "payload": base64.b64encode(
                    serialized
                ).decode("ascii"),
            })

            loop = asyncio.get_running_loop()
            future = loop.create_future()

            self.pending[task_id] = future

            for attempt in range(retries + 1):
                logger.info(
                    "Sending task | task_id=%s | attempt=%s",
                    task_id,
                    attempt + 1,
                )

                self.transport.sendto(packet)

                try:
                    response = await asyncio.wait_for(
                        asyncio.shield(future),
                        timeout,
                    )

                except asyncio.TimeoutError:
                    self.metrics.record_timeout()

                    if attempt == retries:
                        logger.warning(
                            "Task timed out | task_id=%s | attempts=%s",
                            task_id,
                            retries + 1,
                        )

                        raise TimeoutError(
                            f"Task {task_id} timed out"
                        ) from None

                    self.metrics.record_retry()

                    logger.warning(
                        "Retrying task | task_id=%s | next_attempt=%s",
                        task_id,
                        attempt + 2,
                    )

                    continue

                if not response.get("ok"):
                    remotely_cancelled = response.get("cancelled") is True
                    if remotely_cancelled:
                        logger.info(
                            "Remote task cancelled | task_id=%s",
                            task_id,
                        )
                    else:
                        logger.error(
                            "Remote task failed | task_id=%s",
                            task_id,
                        )

                    raise RuntimeError(
                        response.get(
                            "error",
                            "Remote execution failed",
                        )
                    )

                duration = time.perf_counter() - start_time

                self.metrics.record_success(duration)

                logger.info(
                    "Task result delivered | task_id=%s",
                    task_id,
                )

                return response.get("value")

        except (Exception, asyncio.CancelledError):
            duration = time.perf_counter() - start_time

            if remotely_cancelled:
                self.metrics.record_cancellation(duration)
            else:
                self.metrics.record_failure(duration)
            raise

        finally:
            self.pending.pop(task_id, None)

            if future is not None and not future.done():
                future.cancel()

    def connection_lost(self, exc):
        logger.info("Client connection closed")


async def start_worker(port=9998):
    loop = asyncio.get_running_loop()

    return await loop.create_datagram_endpoint(
        Worker,
        local_addr=("127.0.0.1", port),
    )


async def start_client(port=9998):
    loop = asyncio.get_running_loop()

    return await loop.create_datagram_endpoint(
        Client,
        remote_addr=("127.0.0.1", port),
    )
