##########################
##
## Code by Susan
##          padath314
##
##########################

import socket
import sys
from UAP import UAP,Message
import time

SESSION_TIMEOUT = 10  # Adjust this value as needed

def PrintMessage(msg : Message, 
                 alternativeMessage = None,
                 alternativeSequence = None):
        if alternativeMessage:
            msg.message = alternativeMessage
        if alternativeSequence:
            msg.seq = alternativeSequence
        print(f"{hex(msg.sID)} [{msg.seq}] {msg.message}")

class Session:
    def __init__(self, session_id, client_address, server_socket, active_sessions):
        self.session_id = session_id
        self.client_address = client_address
        self.last_activity_time = time.time()
        self.expected_sequence_number = 1
        self.server_socket = server_socket  # Store the server socket
        self.active_sessions = active_sessions  # Store the active sessions dictionary

    def is_hello(self, message):
        return message.command == UAP.CommandEnum.HELLO

    def update_activity_time(self):
        self.last_activity_time = time.time()

    def is_inactive(self):
        return time.time() - self.last_activity_time > SESSION_TIMEOUT

    def process_packet(self, received_message):
        # print(received_message)
        # Extract the sequence number from the received message
        received_sequence_number = received_message.seq

        if received_sequence_number == self.expected_sequence_number:
            # Process the packet as expected
            # print(f"Received packet with sequence number {received_sequence_number}: {received_message.message}")
            PrintMessage(received_message)
            self.expected_sequence_number += 1  # Update the expected sequence number
        elif received_sequence_number < self.expected_sequence_number:
            # Handle out-of-order packet (protocol error)
            # print(f"Received out-of-order packet with sequence number {received_sequence_number}.")
            PrintMessage(received_message, "Message out of order")
            #self.close_session()
        else:
            # Handle missing packets
            for missing_sequence_number in range(self.expected_sequence_number, received_sequence_number):
                # print(f"Lost packet with sequence number {missing_sequence_number}")
                PrintMessage(received_message, 
                             alternativeMessage="Packet Lost",
                             alternativeSequence=missing_sequence_number)
            # Update the expected sequence number
            self.expected_sequence_number = received_sequence_number + 1

    def close_session(self):
        # Send a GOODBYE message to the client
        goodbye_message = Message(UAP.CommandEnum.GOODBYE, 0, self.session_id, "GOODBYE")
        encoded_goodbye_message = goodbye_message.EncodeMessage()
        self.server_socket.sendto(encoded_goodbye_message, self.client_address)
        
        # Remove the session from active_sessions
        del self.active_sessions[self.session_id]

        


def send_goodbye_to_inactive_sessions(active_sessions, server_socket):
    inactive_sessions = [session for session in active_sessions.values() if session.is_inactive()]
    
    for session in inactive_sessions:
        goodbye_message = Message(UAP.CommandEnum.GOODBYE, 0, session.session_id, "GOODBYE")
        encoded_goodbye_message = goodbye_message.EncodeMessage()
        server_socket.sendto(encoded_goodbye_message, session.client_address)
        del active_sessions[session.client_address]


def send_goodbye_to_active_sessions(active_sessions, server_socket):
    goodbye_message = Message(UAP.CommandEnum.GOODBYE, 0, 0, "GOODBYE")  # Create a GOODBYE Message

    for session in active_sessions.values():
        encoded_goodbye_message = goodbye_message.EncodeMessage()  # Encode the GOODBYE Message
        server_socket.sendto(encoded_goodbye_message, session.client_address)

def main(port, host='0.0.0.0'):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (host, port)
    print(f"Waiting on host {host} and port {port}")

    server_socket.bind(server_address)
    active_sessions = {}  # Dictionary to track active sessions

    try:
        while True:
            # print('*')
            data, client_address = server_socket.recvfrom(1024)
            received_message = Message.DecodeMessage(data)
            #print(f"Received data from {client_address}: {received_message}")
            
            if received_message.command == UAP.CommandEnum.HELLO:
                session_id = received_message.sID
                
                if session_id not in active_sessions:
                    new_session = Session(session_id, client_address, server_socket, active_sessions)  # Pass server_socket and active_sessions
                    if not new_session.is_hello(received_message):
                        # Terminate the session if the initial message is not HELLO
                        continue
                    active_sessions[session_id] = new_session
                else:
                    # remove from the dictionary 
                    del active_sessions[session_id]
                    continue

                # Update the session's last activity time
                active_sessions[session_id].update_activity_time()

                # Send a reply HELLO message back to the client
                reply_message = Message(UAP.CommandEnum.HELLO, 0, session_id, "Reply HELLO")
                encoded_reply_message = reply_message.EncodeMessage()
                server_socket.sendto(encoded_reply_message, client_address)
                # print("Replies sent")
                PrintMessage(received_message, "Session Started")

            elif received_message.command == UAP.CommandEnum.DATA:
                session_id = received_message.sID
                if session_id not in active_sessions:
                    # Terminate the session if the DATA message is received without a HELLO
                    continue

                # Update the session's last activity time
                active_sessions[session_id].update_activity_time()

                active_sessions[session_id].process_packet(received_message)
                # Send an ALIVE message in response to the DATA message
                alive_message = Message(UAP.CommandEnum.ALIVE, 0, session_id, "ALIVE")
                encoded_alive_message = alive_message.EncodeMessage()
                server_socket.sendto(encoded_alive_message, client_address)
            
            elif received_message.command == UAP.CommandEnum.GOODBYE:
                #print("\necievd goodbye\n")
                session_id = received_message.sID
                if session_id not in active_sessions:
                    # Terminate the session if the DATA message is received without a HELLO
                    continue
                # Send a GOODBYE message to the client
                goodbye_message = Message(UAP.CommandEnum.GOODBYE, 0, session_id, "GOODBYE")
                encoded_goodbye_message = goodbye_message.EncodeMessage()
                server_socket.sendto(encoded_goodbye_message, client_address)
        
                # Remove the session from active_sessions
                del active_sessions[session_id]

                PrintMessage(received_message, "Closing session")
            
            #print(active_sessions)

    except KeyboardInterrupt:
        print("Server is quitting due to keyboard interrupt.")
    except Exception as e:
        print(e)
    finally:
        # Send GOODBYE message to all active sessions
        send_goodbye_to_active_sessions(active_sessions, server_socket)
        # Close the socket and clean up
        server_socket.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        print("Usage: ThreadedUAPServer.py port [host]")
    elif len(sys.argv) == 2:
        main(int(sys.argv[1]))
    else:
        main(int(sys.argv[1]), sys.argv[2])