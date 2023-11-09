import re

class Request:
    def __init__(self, raw: bytes):
        self.raw = raw
        self.raw_split = raw.split(b"\r\n")
        self.log = self.raw_split[0].decode()

        _, path, _ = self.log.split(" ")
        self.path = path

        host = None
        port = None

        # Check for Host header
        raw_host = re.findall(rb"host: (.*?)\r\n", raw.lower())
        
        # if the host header is found, extract and store the host and port information 
        if raw_host:
            raw_host = raw_host[0].decode()
            host, port_str = raw_host.split(":") if ":" in raw_host else (raw_host, None)

        # Check for host in path
        if not host and "://" in path:
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
    
    def header(self):
        raw_split = self.raw_split[1:]
        _header = dict()
        for line in raw_split:
            if not line:
                continue
            broken_line = line.decode().split(":")
            _header[broken_line[0].lower()] = ":".join(broken_line[1:])
            
        return _header

    def __str__(self):
        return "\n".join([x.decode("utf-8") for x in self.raw_split])