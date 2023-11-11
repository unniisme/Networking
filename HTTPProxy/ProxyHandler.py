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
        self.request = self.raw_split[0]
        self.log = self.request.decode()
        self.body = self.raw[len(self.log):]
        logging.debug(f"Request.raw = {self.raw}")
        logging.debug(f"Request.request = {self.request}")
        logging.debug(f"Request.body = {self.body}")

        self.method, path, self.version = self.log.split(" ")
        self.path = path

        host = None
        port = 80

        # Check for Host header
        raw_host = re.findall(rb"host:\s*(.*?)\r\n", raw.lower())
        
        # if the host header is found, extract and store the host and port information 
        if raw_host:
            raw_host = raw_host[0].decode()
            host, port_str = raw_host.split(":") if ":" in raw_host else (raw_host, None)

        # Check for host in path
        if (not host or not port) and "://" in path:
            path_list = path.split("/")
            if path_list[0] == "http:":
                port = 80
            elif path_list[0] == "https:":
                port = 443

            host_n_port = path_list[2].split(":")
            if len(host_n_port) == 1:
                host = host_n_port[0]
            elif len(host_n_port) == 2:
                host, port_str = host_n_port

            path = f"/{'/'.join(path_list[3:])}"

        # Extract port from port_str
        if port_str:
            port = int(port_str)

        self.host = host
        self.port = port
        logging.info(f"request.host = \"{self.host}\", request.port = {self.port}")

    def Header(self):
        return self.body

    def Request(self):
        return self.log
    
    def GetGeaderDict(self):
        raw_split = self.raw_split[1:]
        _header = dict()
        for line in raw_split:
            if not line:
                continue
            broken_line = line.decode().split(":")
            _header[broken_line[0].lower()] = ":".join(broken_line[1:])
            
        return _header
    
    def IsConnect(self):
        """
        Checks if this request is a CONNECT request
        """
        return self.method == Request.Methods.CONNECT

    def __str__(self):
        return "\n".join([str(x) for x in self.raw_split])


class Response:

    StatusCodes = {
        502 : "HTTP/1.0 502 Bad Gateway\r\n\r\n".encode(),
        200 : "HTTP/1.0 200 OK\r\n\r\n".encode(),
    }