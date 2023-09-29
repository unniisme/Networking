from Network import Client, Server
import time
import threading

class ThreadedServer(Server):

    def _MainLoop(self):
        # data, clientAddr = self.server_socket.recvfrom(1024)
        # if not data:
        #     continue
        # self.HandlePacket(data, clientAddr)

        # Recieve handler
        for thread in self.packetThreads:
            if not thread.is_alive():
                self.packetThreads.remove(thread)
                del thread

        if len(self.packetThreads) > 5:
            return # Only keep 5 simultaneous threads

        packetThread = threading.Thread(target=self.RecievePacket)
        packetThread.daemon = True
        packetThread.start()
        self.packetThreads.append(packetThread)


    def Run(self):
        # Define shared variables 
        self.running = threading.Event()
        self.running.set()

        self.packetThreads = []
        
        try:
            while self.running.is_set():
                self._MainLoop()

        except KeyboardInterrupt:
            pass
        finally:
            self.Exit()

    def Exit(self):
        self.running.clear()

    ### Usables
    def Timer(self):
        time.sleep(self.timeout)

    def StartTimer(self) -> threading.Thread:
        outThread = threading.Thread(target=self.Timer)
        outThread.daemon = True
        return outThread
    

class ThreadedClient(Client):

    def _MainLoop(self):
        try:
            message = input()
            isEOF = False
        except EOFError:
            message = "EOF"
            isEOF = True
        except KeyboardInterrupt:
            message = "KeyboardInterrupt"
            isEOF = True
        if not self.running.is_set():
            return
        packetThread = threading.Thread(target=self.HandlePacket, args=(message,isEOF))
        packetThread.start()


    def Run(self):
        # define shared variables
        self.running = threading.Event()
        self.running.set()

        # Start the packet reciever thread
        self.recieverThread = threading.Thread(target=self.RecievePacket)
        self.recieverThread.daemon = True
        self.recieverThread.start()
        try:
            while self.running.is_set():
                self._MainLoop()
        except ConnectionRefusedError:
            self.Exit("Connection refused")

    def Exit(self, reason):
        print("Exiting. Reason:", reason)
        self.running.clear()
        super().Exit()