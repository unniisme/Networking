from Network import Client, Server
import time
import threading

class ThreadedServer(Server):

    def _MainLoop(self):
        try:
            while self.running.is_set():
                data, _ = self.server_socket.recvfrom(1024)
                if not data:
                    continue
                self.HandlePacket(data)
        except KeyboardInterrupt:
            quit()

    def Start(self):
        # Define shared variables 
        self.running = threading.Event()
        self.running.set()

        # Run threads
        serverThread = threading.Thread(target=self._MainLoop)
        serverThread.start()

        try:
            while True:
                self.HandleInput(input())
        except KeyboardInterrupt:
            self.running.clear()
            quit()

class ThreadedClient(Client):

    def Start(self):
        try:
            while True:
                message = input("Enter a message to send (or type 'exit' to quit): ")
                packetThread = threading.Thread(target=self.HandlePacket, args=(message,))
                packetThread.start()
        except KeyboardInterrupt:
            pass
        finally:
            self.client_socket.close()