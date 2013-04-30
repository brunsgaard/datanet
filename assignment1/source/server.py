#!/usr/bin/env python


import socket
import select
import sys
from datetime import datetime
import errno

CALC_OK_MSG = "200 %f"
CALC_NAN_MSG = "201 NAN"

class Server:
    BUFFER_SIZE = 1024
    def __init__(self, port=50000, listen_queue_size=5):
        """
        Initialize the variables required by the name server.
        """

        self.port = port

        self.server = None #use this variable as the server socket


        # Initialize the socket and data structures needed for the server.
        #
        # Set the socket options to allow reuse of the server address, bind
        # the socket and listen for connections .

    def parse_command(self, command, sock):
        """
        Parse the incomming data and act accordingly.
        """

        tokens = command.strip().split()

        #if PING
        if len(tokens) == 1 and tokens[0] == 'PING':
            pass

        #if CALC
        if len(tokens) == 4 and tokens[0] == 'CALC':
            try:
                num1 = float(tokens[1])
                num2 = float(tokens[3])
            except ValueError as e:
                return CALC_NAN_MSG

            if tokens[1] == '+':
                result = num1 + num2
            elif tokens[1] == '-':
                result = num1 - num2
            elif tokens[1] == '*':
                result = num1 * num2
            elif tokens[1] == '/':
                result = num1 / num2
            else:
               return CALC_NAN_MSG

            return CALC_OK_MSG % result

        #if ECHO
        #the below if is looking at the command string instead of the tokens list to allow for whitespaces
        #since the command variable is not stripped
        if len(command) > 5 and command[:5].upper() == 'ECHO ':
            pass
           # return '300 ' + command[5:]

        return '400 BAD FORMAT'

    def run(self):
        """
        The main loop of the server.
        """
        running = True

        while running:
            # This loop should:
            #
            # - Accept new connections.
            #
            # - Read any socket that wants to send information.
            #
            # - Respond to messages that are received according to the rules in
            # the protocol. Any message that does not adhere to the protocol
            # will trigger an error message
            #
            # - Clean up sockets that are dead.

            # use parse_command() method to parse the messages from the client

            running = False
        # Close the server socket when exiting.

#run the server
if __name__ == "__main__":
    try:
        Server().run()
    except Exception as e:

        print e
