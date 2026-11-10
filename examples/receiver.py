
import socket

HOST = "127.0.0.1"
PORT = 5002

def start_receiver():
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver.bind((HOST, PORT))

    print(f"Node B is listening on {HOST}:{PORT}")

    while True:
        message, address = receiver.recvfrom(1024)

        print(f"Message received from Node A: {message.decode()}")

        receiver.sendto(b"ACK: Message received successfully!", address)

if __name__ == "__main__":
    start_receiver()
