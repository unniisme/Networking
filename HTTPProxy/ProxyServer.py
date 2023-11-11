import socket
import select
import threading
import logging
from ProxyHandler import Request, Response

# Logging
FORMAT = "[%(levelname)-8s][%(asctime)s][%(filename)s:%(lineno)s - %(funcName)13s() ] %(message)s"
logging.basicConfig(format=FORMAT, filename='log/server.log', encoding='utf-8', level=logging.DEBUG)

MAX_CHUNK_SIZE = 16*2048

class ProxyServer:

    def __init__(self, host : str = "localhost", port : int = 8800):
        self.host = host
        self.port = port

        self.client_conn = None
        self.server_conn = None

    def HandleConnection(self, client_conn):
        data = b''
        while not (data[-4:] == b"\r\n\r\n" or data[-3:-1] == b"\n\r\n"):
            data += client_conn.recv(MAX_CHUNK_SIZE)


        request = Request(data)
        print(f">> {request.Request()}")
        logging.debug(request)

        server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_conn.connect((request.host, request.port))
        except Exception as e:
            server_conn.send(Response.StatusCodes[502])
            raise e

        if request.IsConnect():
            client_conn.send(Response.StatusCodes[200]) # Fake connection established
            

            while True:
                triple = select.select([client_conn, server_conn], [], [], 60)[0]
                if not len(triple):
                    logging.warn("Select empty")
                    break
                try:
                    if client_conn in triple:
                        data = client_conn.recv(MAX_CHUNK_SIZE)
                        if not data:
                            break
                        logging.debug(f"[client to server] {data}")
                        server_conn.send(data)
                    if server_conn in triple:
                        data = server_conn.recv(MAX_CHUNK_SIZE)
                        if not data:
                            break
                        logging.debug(f"[server to client] {data}")
                except ConnectionAbortedError as e:
                    logging.error(f"Connection Aborted : {e}")
                    break


        else:
            server_conn.send(request.Request())
            server_conn.send(request.Header())

            data = client_conn.recv(256)
            while data:
                logging.debug(f"[client to server] {data}")
                server_conn.send(data)
                data = client_conn.recv(256)

        data = server_conn.recv(256)
        while data:
            logging.debug(f"[server to client] {data}")
            client_conn.send(data)
            data = server_conn.recv(256)

        server_conn.close()
        client_conn.close()

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

                connectionThread = threading.Thread(target=self.HandleConnection, args=(self.client_conn,))
                connectionThread.daemon = True
                connectionThread.start()
                

        except KeyboardInterrupt:
            logging.info("Closing due to keyboard interrupt")

        finally:
            print("Closing.....")
            self.Close()

    def Close(self):
        if self.client_conn: self.client_conn.close()
        if self.server_conn: self.server_conn.close()
        if self.sock: self.sock.close()

if __name__ == "__main__":

    server = ProxyServer()
    server.Start()