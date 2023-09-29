from Network import Server
from UAP import UAP, Message


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
