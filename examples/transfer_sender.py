import socket
import cloudpickle
import json
import base64


HOST = "127.0.0.1"
PORT = 5002


# Function to transfer
def calculate_total():

    numbers = [100, 200, 300, 400]

    return sum(numbers)


# Serialize the function
serialized_function = cloudpickle.dumps(calculate_total)

# Convert bytes into Base64 text
encoded_function = base64.b64encode(
    serialized_function
).decode()

# Prepare message
message = {
    "function": encoded_function
}

# Convert dictionary into JSON bytes
data = json.dumps(message).encode()


# Create UDP socket
sender = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

sender.settimeout(5)

# Send function to Node B
sender.sendto(data, (HOST, PORT))

print("Serialized function sent to Node B")


try:

    # Receive acknowledgement
    response, address = sender.recvfrom(1024)

    print("Node B response:", response.decode())

except socket.timeout:

    print("No acknowledgement received")

finally:

    sender.close()