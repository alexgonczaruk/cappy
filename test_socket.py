import socket

serverIP = "192.168.2.36"
serverPORT = 8888

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((serverIP, serverPORT))
serverSocket.listen()

print("Waiting for connection")
connectionSocket, addr = serverSocket.accept()
print("connected to client!")

while True:
    message = connectionSocket.recv(1024).decode()
    print("message: ", message)

    connectionSocket.send("hi".encode())