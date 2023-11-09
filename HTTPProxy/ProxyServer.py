import socket
import select
import logging
from ProxyHandler import Request    

# Logging
FORMAT = "[%(levelname)-8s][%(asctime)s][%(filename)s:%(lineno)s - %(funcName)13s() ] %(message)s"
logging.basicConfig(format=FORMAT, filename='log/server.log', encoding='utf-8', level=logging.INFO)

MAX_CHUNK_SIZE = 16*2048

class ProxyServer:

    def __init__(self, host : str = "localhost", port : int = 8800):
        self.host = host
        self.port = port

        self.client_conn = None
        self.server_conn = None

    def Start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print(f"Listening at: http://{self.host}:{self.port}")
        logging.info(f"Listening at: http://{self.host}:{self.port}")

        try:
            while True:
                self.client_conn, client_addr = self.sock.accept()
                logging.info(f"Accepted connection from {client_addr}")
                
                try:
                    data = b''
                    while not data:
                        data = self.client_conn.recv(MAX_CHUNK_SIZE)


                    request = Request(data)
                    print(request)
                    logging.debug(request)

                    self.server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    logging.info(f"Server : {request.host, request.port}")
                    self.server_conn.connect((request.host, request.port))

                    self.client_conn.send(b"HTTP/1.1 200 Connection Established\r\n\r\n") # Fake connection established
                    self.server_conn.send(data)

                    while True:
                        triple = select.select([self.client_conn, self.server_conn], [], [], 60)[0]
                        if not len(triple):
                            logging.warn("Select empty")
                            break
                        try:
                            if self.client_conn in triple:
                                data = self.client_conn.recv(MAX_CHUNK_SIZE)
                                if not data:
                                    break
                                print("[Client to Server]\n", Request(data))
                                self.server_conn.send(data)
                            if self.server_conn in triple:
                                data = self.server_conn.recv(MAX_CHUNK_SIZE)
                                if not data:
                                    break
                                print("[Server to Client]\n", Request(data))
                                self.client_conn.send(data)     
                        except ConnectionAbortedError as e:
                            logging.error(f"Connection Aborted : {e}")
                            break

                except Exception as e:
                    logging.error(f"Error : {e}")
                    continue

        except KeyboardInterrupt:
            print("Closing.....")
            logging.info("Closing due to keyboard interrupt")
            self.Close()

    def Close(self):
        if self.client_conn: self.client_conn.close()
        if self.server_conn: self.server_conn.close()
        if self.sock: self.sock.close()

if __name__ == "__main__":

    server = ProxyServer()
    server.Start()