from Network import Server, Client
import asyncio

class AsyncServer(Server):

    async def AsyncStart(self):
        while True:
            # Get data using event loop
            data = await self.loop.sock_recv(self.server_socket, 1024)
            if not data:
                continue
            self.HandlePacket(data)

    def Start(self):
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

    def Start(self):
        try:
            # Run main function asynchronously
            asyncio.run(self.AsyncStart())
        except KeyboardInterrupt:
            pass
        finally:
            self.client_socket.close()
