import socket

class Server:

    def __init__(self, host, port, timeout=5):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((host, port))
        print(f"Server waiting on {host}:{port}")

        self.timeout = timeout

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

    # To be implemented in async or thread
    def StartTimer(self):
        """
        Start an asynchronous/parallel timer that will call the 
        function self.HandleTimer once timeout
        """
        pass

    def HandleTimer(self):
        """
        Function called when timer times out
        """
        pass

    def HandleInput(self, message):
        """
        For the main server to handle console inputs
        """


class Client:
    def __init__(self, host, port, timeout=5):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")

        self.timeout = timeout

    def SendPacket(self, message):
        # Override
        self.client_socket.sendall(message.encode('utf-8'))

    def HandlePacket(self, message):
        # Override
        self.SendPacket(message)

    def Start(self):
        try:
            while True:
                message = input("Enter a message to send (or type 'exit' to quit): ")
                self.HandlePacket(message)
        except KeyboardInterrupt:
            pass
        finally:
            self.client_socket.close()

    # To be implemented in async or thread
    def StartTimer(self):
        """
        Start an asynchronous/parallel timer that will call the 
        function self.HandleTimer once timeout
        """
        pass

    def HandleTimer(self):
        """
        Function called when timer times out
        """
        pass
