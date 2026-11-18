
import socket
import cloudpickle

HOST = "127.0.0.1"
PORT = 9999

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
    server.bind((HOST, PORT))
    server.settimeout(60)

    print("Node B: Waiting for function...")

    try:
        data, address = server.recvfrom(65507)

        # Trusted localhost demonstration only
        function, args = cloudpickle.loads(data)

        print("Function received:", function.__name__)

        result = function(*args)

        print("Execution result:", result)

        server.sendto(cloudpickle.dumps(result), address)
        print("Result sent to Node A")

    except socket.timeout:
        print("Timeout waiting for function")
    except Exception as error:
        print("Error:", error)
