

class UAP:

    class CommandEnum:
        HELLO = 0
        DATA = 1
        ALIVE = 2
        GOODBYE = 3

    MAGIC_NUMBER = 0xC461 
    
    _lastnBits = lambda n,x : x >> (x.bit_length() - n) # Get last n bits of x
    _firstnBits = lambda n,x : x & ((1 << (n+1))-1)     # Get first n bits of x

    HeaderBits = lambda x: UAP._lastnBits(96, x)
    MessageBits = lambda x: UAP._firstnBits(x.bit_length()-96, x)

    MASKS = {
        "MAGIC"     : 0xffff00000000000000000000,
        "VERSION"   : 0x0000ff000000000000000000,
        "COMMAND"   : 0x000000ff0000000000000000,
        "SEQUENCE"  : 0x00000000ffffffff00000000,
        "SESSION"   : 0x0000000000000000ffffffff,
    }

    SHIFTS = {
        "MAGIC"     : 4*20,
        "VERSION"   : 4*18,
        "COMMAND"   : 4*16,
        "SEQUENCE"  : 4*8,
        "SESSION"   : 4*0,
    }


    _GetBits = lambda x, mode: (UAP.HeaderBits(x) & UAP.MASKS[mode]) >>  UAP.SHIFTS[mode]

    MagicBits = lambda x: UAP._GetBits(x, "MAGIC")
    VersionBits = lambda x: UAP._GetBits(x, "VERSION")
    CommandBits = lambda x: UAP._GetBits(x, "COMMAND")
    SequenceBits = lambda x: UAP._GetBits(x, "SEQUENCE")
    SessionBits = lambda x: UAP._GetBits(x, "SESSION")

class Message:

    def __init__(
            self,
            command : UAP.CommandEnum, 
            sequenceNo : int, 
            sessionID : int, 
            message : str
        ):
        self.command = command
        self.seq = sequenceNo
        self.sID = sessionID
        self.message = message
        self.version = 1
        self.magic = UAP.MAGIC_NUMBER

    def __str__(self):
        outstring = ""
        outstring += f"| {self.magic} "
        outstring += f"| {self.version} "
        outstring += f"| {self.command} "
        outstring += f"| {self.seq} "
        outstring += f"| {self.sID} "
        outstring += f"| {self.message} |"
        return outstring
    
    def __repr__(self):
        return str(self)
        
    def _EncodeMessage(
            command : UAP.CommandEnum, 
            sequenceNo : int, 
            sessionID : int, 
            message : str
        ) -> bytes:

        headerNum = UAP.MAGIC_NUMBER << UAP.SHIFTS["MAGIC"]
        headerNum += 1 << UAP.SHIFTS["VERSION"]
        headerNum += command << UAP.SHIFTS["COMMAND"]
        headerNum += sequenceNo << UAP.SHIFTS["SEQUENCE"]
        headerNum += sessionID << UAP.SHIFTS["SESSION"]
        
        return headerNum.to_bytes(24, 'big') + message.encode()

    def EncodeMessage(self) -> bytes:
        return Message._EncodeMessage(self.command, self.seq, self.sID, self.message)
    
    def DecodeMessage(messages : bytes) -> "Message":
        message = int.from_bytes(messages, "big")

        magic = UAP.MagicBits(message)
        version = UAP.VersionBits(message)

        if magic != UAP.MAGIC_NUMBER:
            raise ValueError(f"Magic number does not match. Obtained magic number : {magic}")

        if version != 1: # This is a v1 agent
            raise ValueError(f"Version mismatch. Obtained version : {version}")
        
        command = UAP.CommandBits(message)
        sequenceNo = UAP.SequenceBits(message)
        sessionID = UAP.SessionBits(message)
        message = (UAP.MessageBits(message).to_bytes(message.bit_length()//4 + 1, "big")).decode("utf-8")

        return Message(command, sequenceNo, sessionID, message)
    

if __name__ == "__main__":

    m = Message(1, 0, 0, "Hello world")

    print("Input Message:")
    print(m)

    m_enc = m.EncodeMessage()

    m_dec = Message.DecodeMessage(m_enc)

    print("Output Message:")
    print(m_dec)


