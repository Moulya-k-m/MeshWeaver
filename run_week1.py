
import subprocess
import sys
import time


PYTHON = sys.executable


def start_receiver(file_name):
    return subprocess.Popen(
        [PYTHON, f"examples/{file_name}"]
    )


def main():

    processes = []

    try:

        print("\n===== DAY 1: UDP COMMUNICATION =====")

        processes.append(start_receiver("receiver.py"))
        time.sleep(1)

        subprocess.run(
            [PYTHON, "examples/sender.py"]
        )

        print("\n===== DAY 2: ASYNC UDP =====")

        processes.append(start_receiver("async_receiver.py"))
        time.sleep(1)

        subprocess.run(
            [PYTHON, "examples/async_sender.py"]
        )

        print("\n===== DAY 3: SERIALIZATION =====")

        subprocess.run(
            [PYTHON, "examples/serialization_demo.py"]
        )

        print("\n===== DAY 4: FUNCTION TRANSFER =====")

        processes.append(start_receiver("transfer_receiver.py"))
        time.sleep(1)

        subprocess.run(
            [PYTHON, "examples/transfer_sender.py"]
        )

        print("\n===== DAY 5: REMOTE EXECUTION =====")

        processes.append(start_receiver("remote_worker.py"))
        time.sleep(1)

        subprocess.run(
            [PYTHON, "examples/remote_sender.py"]
        )

        print("\n===== WEEK 1 COMPLETED =====")

    finally:

        for process in processes:
            process.terminate()

        for process in processes:
            process.wait()


if __name__ == "__main__":
    main()
