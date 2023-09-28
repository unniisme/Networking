from Network import Server, Client
from UAP import Message, UAP
import random

class UAPServer(Server):

    def __init__(self, server : Server):
        self.instance = server
        self.state = 1 # Recieve
        ## State 0 is done

        self.instance.DecodePacket = self.DecodePacket
        self.instance.HandlePacket = self.HandlePacket
        self.instance.RecievePacket = self.RecievePacket

    def DecodePacket(self, data: bytes) -> Message:
        return Message.DecodeMessage(data)
    
    def PrintMessage(self, msg : Message):
        print(f"{hex(msg.sID)} [{msg.seq}] {msg.message}")
    
    def HandlePacket(self, data, clientAddr):
        if self.state == 0:
            self.instance.Exit()
        try:
            msg = self.DecodePacket(data)

            if msg.command == UAP.CommandEnum.HELLO:
                ## Set timer

                # Save maintain session ID - sequence No.
                self.sessionSequenceDict[msg.sID] = msg.seq
                # Return Hello packet (same packet here)
                self.instance.server_socket.sendto(data, clientAddr)

                msg.message = "Session created"
                self.PrintMessage(msg)

            elif msg.command == UAP.CommandEnum.ALIVE:
                pass # Reset timer

            elif msg.command == UAP.CommandEnum.DATA:
                if msg.seq == self.sessionSequenceDict[msg.sID] + 1: # In Sequence
                    self.PrintMessage(msg)
                    self.sessionSequenceDict[msg.sID] += 1
                elif msg.seq < self.sessionSequenceDict[msg.sID] + 1:
                    self.PrintMessage(Message(
                        msg.command, msg.seq, msg.sID,
                        "Duplicate Packet"
                    ))
                else:
                    while msg.seq > self.sessionSequenceDict[msg.sID] + 1: # Packet lost
                        self.PrintMessage(Message(
                            msg.command, 
                            self.sessionSequenceDict[msg.sID] + 1, 
                            msg.sID,
                            "Lost packet!"
                        ))
                        self.sessionSequenceDict[msg.sID] += 1
                self.instance.server_socket.sendto(Message(
                    UAP.CommandEnum.ALIVE,
                    msg.seq,
                    msg.sID,
                    "ALIVE"
                ).EncodeMessage(), clientAddr)

            elif msg.command == UAP.CommandEnum.GOODBYE:
                self.PrintMessage(Message(
                    msg.command, msg.seq, msg.sID,
                    "GOODBYE from client."
                ))

                # Return the goodbye packet
                self.instance.server_socket.sendto(data, clientAddr)
            else:
                raise ValueError(f"Unknown command : {msg.command}")
        except ValueError as e:
            import sys
            print(e, sys.stderr)

    def RecievePacket(self):
        data, clientAddr = self.instance.server_socket.recvfrom(1024)
        if data:
            self.HandlePacket(data, clientAddr)
        return
        
    def Run(self):
        self.sessionSequenceDict = {}

        return self.instance.Run()
    

class UAPClient(Client):

    STATES = {
        "Hello wait"    : 0,
        "Ready"         : 1,
        "Ready Timer"   : 2,
        "Closing"       : 3,
        ""              : 4,
    }

    def __init__(self, client : Client):
        self.instance = client
        self.state = UAPClient.STATES["Hello wait"]

        self.instance.SendPacket = self.SendPacket
        self.instance.HandlePacket = self.HandlePacket
        self.instance.RecievePacket = self.RecievePacket


    def SendPacket(self, message : Message):
        self.instance.client_socket.sendall(message.EncodeMessage())
        self.seq += 1

    def HandlePacket(self, message : str, isEOF : bool = False):
        if isEOF:
            self.SendPacket(Message(
                UAP.CommandEnum.GOODBYE,
                self.seq,
                self.sID,
                "EOF"
            ))
            while self.instance.running.is_set():
                pass
            return
        if message == "q":
            message = Message(
                UAP.CommandEnum.GOODBYE,
                self.seq,
                self.sID,
                ""
            )
        else:
            message = Message(
                UAP.CommandEnum.DATA, 
                self.seq, 
                self.sID, 
                message
            )
        self.SendPacket(message)

    def RecievePacket(self):
        while self.instance.running.is_set():
            data, _ = self.instance.client_socket.recvfrom(1024)
            msg = Message.DecodeMessage(data)
            if msg.command == UAP.CommandEnum.GOODBYE:
                self.Exit("GOODBYE from server")

    def Run(self):
        # Session start hello
        self.sID = random.getrandbits(32)
        self.seq = 0
        helloMessage = Message(UAP.CommandEnum.HELLO, self.seq, self.sID, "")
        self.SendPacket(helloMessage)

        # Wait for hello
        while True:
            data, _ = self.instance.client_socket.recvfrom(1024)
            msg = Message.DecodeMessage(data)
            if msg.sID == self.sID and msg.command == UAP.CommandEnum.HELLO:
                self.state = UAPClient.STATES["Ready"]
                break

        self.instance.Run()

    def Exit(self, reason):
        self.instance.Exit(reason)
        