import socket
import cloudpickle
import json
import base64


HOST = "127.0.0.1"
PORT = 5003


# Create UDP socket
worker = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

worker.bind((HOST, PORT))

print("Remote worker is running...")


while True:

    # Receive function from Node A
    data, address = worker.recvfrom(65507)

    try:

        # Convert received JSON
        message = json.loads(data.decode())

        # Get serialized function
        encoded_function = message["function"]

        # Decode Base64
        serialized_function = base64.b64decode(
            encoded_function
        )

        # Restore Python function
        received_function = cloudpickle.loads(
            serialized_function
        )

        print("Function received")

        # Execute the function
        result = received_function()

        print("Function executed successfully")

        # Prepare result response
        response = {
            "status": "success",
            "result": result
        }

    except Exception as error:

        response = {
            "status": "error",
            "message": str(error)
        }

    # Send result back to Node A
    worker.sendto(
        json.dumps(response).encode(),
        address
    )