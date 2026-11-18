
import socket
import cloudpickle

HOST = "127.0.0.1"
PORT = 9999


def calculate_square(number):
    return number * number


task = (calculate_square, (25,))
serialized_task = cloudpickle.dumps(task)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
    client.settimeout(10)

    client.sendto(serialized_task, (HOST, PORT))
    print("Node A: Function sent")

    try:
        response, address = client.recvfrom(65507)
        result = cloudpickle.loads(response)

        print("Remote execution successful")
        print("Result received:", result)

    except socket.timeout:
        print("Timeout waiting for result")
