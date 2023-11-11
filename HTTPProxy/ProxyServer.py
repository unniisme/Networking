import socket
import threading
import logging
from ProxyHandler import Request, Response

# Logging
FORMAT = "[%(levelname)-8s][%(asctime)s][%(filename)s:%(lineno)s - %(funcName)13s()] %(message)s"
logging.basicConfig(format=FORMAT, filename='log/server.log', encoding='utf-8', level=logging.INFO)

MAX_CHUNK_SIZE = 16*2048

class ProxyServer:

    def __init__(self, host : str, port : int):
        self.host = host
        self.port = port

        self.client_conn = None
        self.server_conn = None

    def MainThread(self, client_conn):
        # Recieve outgoing data from browser
        data = b''
        while not (data[-4:] == b"\r\n\r\n" or data[-3:-1] == b"\n\r\n"):
            data += client_conn.recv(MAX_CHUNK_SIZE)

        # Process the data
        request = Request(data)
        print(f">> {request.Request().decode()}")
        logging.debug(f"request:\n{request}")

        # Try to connect to the requested server
        server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_conn.connect((request.host, request.port))
        except Exception as e:
            server_conn.send(Response.StatusCodes[502])
            logging.error(f"Couldn't connect to {request.host}:{request.port}\
                          Exiting with exception : {e}")
            client_conn.close()
            return

        # If request is of type CONNECT
        if request.IsConnect():
            # Send response code
            client_conn.send(Response.StatusCodes[200]) # Fake connection established

            # Start threads to usher TCP connection between browser and server
            sendThread = threading.Thread(target=self.ConnectionThread, args=(client_conn, server_conn))            
            recieveThread = threading.Thread(target=self.ConnectionThread, args=(server_conn, client_conn))
            sendThread.daemon = True
            recieveThread.daemon = True
            logging.info(f"Staring sendThread {sendThread}")
            sendThread.start()

            logging.info(f"Staring recieveThread {sendThread}")
            recieveThread.start()            

        # If request if GET
        else:
            server_conn.send(request.Request())
            server_conn.send(request.Header())

            # Send data to server
            data = client_conn.recv(256)
            while data:
                logging.debug(f"[client to server] {data}")
                server_conn.send(data)
                data = client_conn.recv(256)

            # Recieve data from server
            data = server_conn.recv(256)
            while data:
                logging.debug(f"[server to client] {data}")
                client_conn.send(data)
                data = server_conn.recv(256)

            server_conn.close()
            client_conn.close()

    def ConnectionThread(self, source_conn : socket.socket, dest_conn : socket.socket):
        # Thread that simply channels connection between any 2 sockets

        logging.info(f"[{threading.get_ident()}] Starting thread")        
        
        while True:
            try:
                data = source_conn.recv(256)
                if not data:
                    break
                logging.debug(f"[{threading.get_ident()}] {data}")
                dest_conn.send(data)
            except ConnectionAbortedError:
                break

        logging.info(f"[{threading.get_ident()}] Closing thread")
                

    def Start(self):
        # Start proxy socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print(f"Proxy listening at: http://{self.host}:{self.port}")
        logging.info(f"Proxy listening at: http://{self.host}:{self.port}")

        try:
            while True:
                # Accept each connection from browser each 
                self.client_conn, client_addr = self.sock.accept()
                logging.info(f"Accepted connection from {client_addr}")

                # Start a thread for each connection
                connectionThread = threading.Thread(target=self.MainThread, args=(self.client_conn,))
                connectionThread.daemon = True
                connectionThread.start()
                

        except KeyboardInterrupt:
            logging.info("Closing due to keyboard interrupt")

        finally:
            self.Close()
            print("Closing.....")

    def Close(self):
        self.sock.close()
        exit()

if __name__ == "__main__":
    from sys import argv



    if len(argv) == 1:
        host = 'localhost'
        port = 8800
    elif len(argv) == 2:
        host = 'localhost'
        port = int(argv[1])
    elif len(argv) == 3:
        host = argv[1]
        port = int(argv[2])
    else:
        if len(argv) > 3:
            print("Usage: \n\tProxyServer.py\n\tProxyServer.py [port]\n\tProxyServer.py [host] [port]")
        exit()
            

    server = ProxyServer(host, port)
    server.Start()