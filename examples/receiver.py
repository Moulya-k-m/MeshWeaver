import socket

HOST = "127.0.0.1"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind((HOST, PORT))

print("Node B is waiting for messages...")

while True:

    data, address = server.recvfrom(1024)

    message = data.decode()

    print("Received:", message)

    response = "ACK: Message received successfully"

    server.sendto(response.encode(), address)