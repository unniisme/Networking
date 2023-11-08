##########################
##
## Code by Susan
##          padath314
##
##########################

import asyncio 
from UAP import Message,UAP
from Network import Client
import random
import time


sID = random.getrandbits(32)
seq = 0

isRunning = False
timerStart = 0
timeout = 10

STATES = {
        "Hello wait": 0,
        "Ready": 1,
        "Ready Timer": 2,
        "Closing": 3,
        "": 4,
    }

currState = STATES["Hello wait"]
    
async def sendPacket(client : Client,message : Message):
    global seq
    client.SendPacket(message.EncodeMessage())
    seq +=1

async def ReceivePacket(client):
    global isRunning, timerStart , currState
    client.client_socket.settimeout(None)
    while isRunning:
        data, _ = await asyncio.to_thread(client.client_socket.recvfrom, 1024)
        msg = Message.DecodeMessage(data)
        if msg.command == UAP.CommandEnum.HELLO:
            print("Received Hello from server")
        if msg.command == UAP.CommandEnum.GOODBYE:
            isRunning = False
            print("GOODBYE from server")
        if msg.command == UAP.CommandEnum.ALIVE:
            if currState == STATES["Ready Timer"]:
                currState = STATES["Ready"]
                timerStart = time.time()

async def main(host, port):
    
    global isRunning, timerStart, currState

    # Initialize the client
    client = Client(host, port)
    
    helloMessage = Message(UAP.CommandEnum.HELLO, seq, sID, "Hii")
    await sendPacket(client,helloMessage)
    client.client_socket.settimeout(timeout)

    recieverThread = None

    # Wait for hello
    try:
        while True:
            try:
                data, _ = await asyncio.to_thread(client.client_socket.recvfrom, 1024)
                if not data:
                    continue
                msg = Message.DecodeMessage(data)
                if msg.sID == sID and msg.command == UAP.CommandEnum.HELLO:
                    currState = STATES["Ready"]
                    break
            except TimeoutError:
                currState = STATES["Closing"]

        isRunning = True

        recieverThread = asyncio.create_task(ReceivePacket(client))
        
        timerStart = time.time()
        while currState in [STATES["Ready"],STATES["Ready Timer"]]:
            try:
                m  = await asyncio.to_thread(input)
            except EOFError:
                currState = STATES["Closing"]
                break
            except KeyboardInterrupt : 
                await sendPacket(client, Message(UAP.CommandEnum.GOODBYE, seq, sID, "POi"))
                currState = STATES["Closing"]
                break

            if time.time() - timerStart > timeout and currState is STATES["Ready Timer"]:
                print(time.time() - timerStart, timeout)
                currState = STATES["Closing"]
                break
            
            if not isRunning:
                currState = STATES["Closing"]
                break
            
            message = Message(UAP.CommandEnum.DATA,seq,sID,m)
            await sendPacket(client,message)
            currState = STATES["Ready Timer"]

        if currState == STATES["Closing"]:
            await sendPacket(client, Message(UAP.CommandEnum.GOODBYE, seq, sID, "POi"))
        
        while isRunning:
            if time.time() - timerStart >timeout:
                isRunning = False

    except ConnectionRefusedError:
        print("Connection Refused")
    except Exception as e:
        print(e)
    finally:
        isRunning = False
        if recieverThread:
            recieverThread.cancel()
        client.Exit()
    

    # Close the client
    client.Exit()

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: UAPClient.py host port")
        quit()

    elif len(sys.argv) == 3: 
        asyncio.run(main(sys.argv[1], int(sys.argv[2])))