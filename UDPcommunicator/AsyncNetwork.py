from Network import Server, Client
import asyncio

class AsyncServer(Server):

    async def RecievePacket(self):
        data, clientAddr = self.server_socket.recvfrom(1024)
        while not data:
            data, clientAddr = self.server_socket.recvfrom(1024)
        return data, clientAddr

    async def AsyncStart(self):
        while True:
            # Get data using event loop
            # client, _ = await self.loop.sock_accept(self.server_socket)
            data, clientAddr = await self.RecievePacket()
            self.HandlePacket(data, clientAddr)

    def Run(self):
        self.loop = asyncio.get_event_loop()
        try:
            # Run main function asynchronously
            asyncio.run(self.AsyncStart())
        except KeyboardInterrupt:
            pass
    
class AsyncClient(Client):
    
    async def AsyncStart(self):
        while True:
            self.HandlePacket()

    def Run(self):
        try:
            # Run main function asynchronously
            asyncio.run(self.AsyncStart())
        except KeyboardInterrupt:
            pass
        finally:
            self.client_socket.close()
