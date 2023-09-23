import socket

class Server:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((host, port))
        print(f"Server waiting on {host}:{port}")

    def DecodePacket(self, data : bytes):
        # Override
        return data.decode('utf-8')
    
    def HandlePacket(self, data):
        # Override
        print(self.DecodePacket(data))

    def Start(self):
        while True:
            data, _ = self.server_socket.recvfrom(1024)
            if not data:
                continue
            self.HandlePacket(data)


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")

    def SendPacket(self, message):
        # Override
        self.client_socket.sendall(message.encode('utf-8'))

    def HandlePacket(self):
        # Override
        message = input("Enter a message to send (or type 'exit' to quit): ")
        self.SendPacket(message)

    def Start(self):
        try:
            while True:
                self.HandlePacket()
        except KeyboardInterrupt:
            pass
        finally:
            self.client_socket.close()
