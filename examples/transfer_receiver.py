import socket
import json
import base64

HOST = "127.0.0.1"
PORT = 5002

# Create UDP socket
receiver = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

# Bind the receiver to an address
receiver.bind((HOST, PORT))

print("Node B waiting for serialized function...")

while True:

    # Receive data
    data, address = receiver.recvfrom(65507)

    # Convert JSON bytes into dictionary
    message = json.loads(data.decode())

    # Extract serialized function
    encoded_function = message["function"]

    # Convert Base64 back into bytes
    serialized_function = base64.b64decode(encoded_function)

    # Save serialized function
    with open("received_function.pkl", "wb") as file:

        file.write(serialized_function)

    print("Function received successfully")

    print("Saved as received_function.pkl")

    # Send acknowledgement
    response = {
        "status": "success",
        "message": "Function received successfully"
    }

    receiver.sendto(
        json.dumps(response).encode(),
        address
    )