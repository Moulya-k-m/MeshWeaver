import socket
import cloudpickle
import json
import base64


HOST = "127.0.0.1"
PORT = 5003


# Function to execute remotely
def multiply_numbers():

    a = 20
    b = 50

    return a * b


# Serialize function
serialized_function = cloudpickle.dumps(
    multiply_numbers
)

# Convert bytes to Base64
encoded_function = base64.b64encode(
    serialized_function
).decode()

# Prepare message
message = {
    "function": encoded_function
}

data = json.dumps(message).encode()


# Create UDP socket
sender = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

sender.settimeout(5)

# Send function to Node B
sender.sendto(data, (HOST, PORT))

print("Function sent to remote worker")


try:

    # Receive result
    response, address = sender.recvfrom(1024)

    result_data = json.loads(response.decode())

    if result_data["status"] == "success":

        print("Remote execution successful")

        print("Result:", result_data["result"])

    else:

        print("Remote execution failed")

        print("Error:", result_data["message"])

except socket.timeout:

    print("Remote worker did not respond")

finally:

    sender.close()