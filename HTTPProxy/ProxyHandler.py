import re
import logging

class Request:

    class Methods:
        CONNECT = "CONNECT"
        GET = "GET"
        POST = "POST"

    def __init__(self, raw: bytes):
        self.raw = raw
        self.raw_split = raw.split(b"\r\n")
        self.log = self.raw_split[0].decode()
        self.body = self.raw[len(self.log):]
        logging.info(f"Request.raw = {self.raw}")
        logging.info(f"Request.body = {self.body}")

        ### Request details
        self.method, self.path, self.version = self.log.split(" ")

        # Lower HTTP version
        self.version = "HTTP/1.0"

        host = ""
        port = 80
        header = "" 

        for raw_line in self.raw_split[1:]:
            line = raw_line.decode()

            # Check for Host header
            if "host" in line.lower():
                raw_host = raw_line.split(b':', 1)[1].decode().strip()

                # if the host header is found, extract and store the host and port information 
                if raw_host:
                    host, port_str = raw_host.split(":") if ":" in raw_host else (raw_host, None)

                # Check for host in path
                if (not host or not port) and "://" in self.path:
                    path_list = self.path.split("/")
                    if path_list[0] == "http:":
                        port = 80
                    elif path_list[0] == "https:":
                        port = 443

                    host_n_port = path_list[2].split(":")
                    if len(host_n_port) == 1:
                        host = host_n_port[0]
                    elif len(host_n_port) == 2:
                        host, port_str = host_n_port

                    self.path = f"/{'/'.join(path_list[3:])}"

                # Extract port from port_str
                if port_str:
                    port = int(port_str)

            if "keep-alive" in line.lower():
                line = self.OverrideKeepAlive(line)

            header += line + "\r\n"


        self.host = host
        self.port = port

        self.header = header.encode()
        logging.info(f"Request.request = {self.Request()}")
        logging.info(f"Request.header = {self.header}")
        logging.info(f"Request.host = \"{self.host}\", Request.port = {self.port}")

    def Header(self):
        return self.header

    def Request(self):
        return f"{self.method} {self.path} {self.version}".encode()

    def GetHeaderDict(self):
        return self.headerDict
    
    def IsConnect(self):
        """
        Checks if this request is a CONNECT request
        """
        return self.method == Request.Methods.CONNECT

    def __str__(self):
        return "\n".join([str(x) for x in self.raw_split])
    

    ## Request overrides
    def OverrideKeepAlive(self, line : str) -> str:
        return line.replace("keep-alive", "close")


class Response:

    StatusCodes = {
        502 : "HTTP/1.0 502 Bad Gateway\r\n\r\n".encode(),
        200 : "HTTP/1.0 200 OK\r\n\r\n".encode(),
    }


    