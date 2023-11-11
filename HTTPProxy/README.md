# HTTP Proxy using python

### Functionalities
- Changes the HTTP version of all requests to HTTP/1.0
- Changes all keep-alive requests to close
- Channels all data from CONNECT or GET requests


### Running
run using
```
$ ./proxy [host] [port]
$ ./proxy [port]
$ ./proxt
```
default host is localhost, default port is 8800

### Logging
Log messages will be generated in `/log/server.log`