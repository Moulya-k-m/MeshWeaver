
import socket

HOST = "127.0.0.1"
PORT = 5002

def send_message():
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender.settimeout(5)

    message = "Hello from MeshWeaver Node A!"

    sender.sendto(message.encode(), (HOST, PORT))
    print("Message sent to Node B!")

    response, address = sender.recvfrom(1024)

    print("Response from Node B:", response.decode())

    sender.close()

if __name__ == "__main__":
    send_message()
