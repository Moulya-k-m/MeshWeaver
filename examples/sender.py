import socket

HOST = "127.0.0.1"
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

message = "Hello from Node A"

client.sendto(message.encode(), (HOST, PORT))

data, address = client.recvfrom(1024)

print("Response from Node B:", data.decode())

client.close()