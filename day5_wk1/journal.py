
import json
import os


class Journal:
    """Append-only JSON-lines log of task changes."""

    def __init__(self, path):
        self.path = path

        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        self._file = None

    def load(self) -> dict:
        """Replay the journal and return {task_id: task_dict}."""

        tasks = {}

        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        rec = json.loads(line)

                        if rec.get("op") == "task":
                            task = rec["task"]
                            tasks[task["task_id"]] = task

                        elif rec.get("op") == "update":
                            task_id = rec["task_id"]

                            if task_id in tasks:
                                tasks[task_id].update(rec["fields"])

                    except (ValueError, KeyError, TypeError):
                        continue

        self._file = open(self.path, "a", encoding="utf-8")

        return tasks

    def write(self, record: dict):
        """Append one record to the journal."""

        if self._file is None:
            raise RuntimeError("Journal is not open. Call load() first.")

        self._file.write(json.dumps(record) + "\n")
        self._file.flush()
        os.fsync(self._file.fileno())

    def close(self):
        """Close the journal safely."""

        if self._file:
            self._file.close()
            self._file = None
