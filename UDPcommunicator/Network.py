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
    
    def HandlePacket(self, data, clientAddr):
        # Override
        print(clientAddr, ":", self.DecodePacket(data))

    def Run(self):
        while True:
            self.RecievePacket()
            # Add other async/threaded methods here

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
        pass

    def RecievePacket(self):
        """
        Function to recieve a packet
        """
        data, clientAddr = self.server_socket.recvfrom(1024)
        while not data:
            data, clientAddr = self.server_socket.recvfrom(1024)
        self.HandlePacket(data, clientAddr)

    def Exit(self):
        """
        Gracefully shut down server. Function should be callable by any thread/async event
        """
        pass
    


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

    def HandlePacket(self, message : str, isEOF : bool = False):
        # Override
        self.SendPacket(message)

    def Run(self):
        try:
            while True:
                try:
                    message = input()
                    self.HandlePacket(message)
                except EOFError:
                    self.HandlePacket("", isEOF=True)
        except KeyboardInterrupt:
            pass
        finally:
            self.Exit()

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

    def RecievePacket(self):
        """
        Function to recieve a packet
        """
        pass

    def Exit(self):
        """
        Call to gracefully shut down client
        """
        self.client_socket.close()


