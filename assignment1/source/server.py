#!/usr/bin/env python

import socket
import select
import sys
from datetime import datetime
import errno

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
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind( ('0.0.0.0', self.port) )
        self.server.listen(0)

    def parse_command(self, command, sock):
        """
        Parse the incomming data and act accordingly.
        """

        tokens = command.strip().split()

        #if PING
        if len(tokens) == 1 and tokens[0] == 'PING':
            return '100 PONG %s %s' % (sock.getpeername(), datetime.now().strftime("%H:%M:%S"))

        #if CALC
        if len(tokens) == 4 and tokens[0] == 'CALC':
            try:
                num1 = float(tokens[1])
                num2 = float(tokens[3])
            except ValueError as e:
                return CALC_NAN_MSG

            if tokens[2] == '+':
                result = num1 + num2
            elif tokens[2] == '-':
                result = num1 - num2
            elif tokens[2] == '*':
                result = num1 * num2
            elif tokens[2] == '/':
                result = num1 / num2
            else:
               return CALC_NAN_MSG

            if result == int(result):
                result = int(result)

            return "200 EQUALS %s" % str(result)

        #if ECHO
        #the below if is looking at the command string instead of the tokens list to allow for whitespaces
        #since the command variable is not stripped
        if len(command) > 5 and command[:5].upper() == 'ECHO ':
            return '300 ' + command[5:]

        return '400 BAD FORMAT'

    def run(self):
        """
        The main loop of the server.
        """
        running = True

        while running:
            clientsock, addr = self.server.accept()

            while True:
                command = clientsock.recv(self.BUFFER_SIZE)
                if not command:
                    break;
                response = self.parse_command(command, clientsock)
                clientsock.send(response)

            clientsock.close()

        running = False
        self.server.close()

#run the server
if __name__ == "__main__":
    try:
        server = Server()
        server.run()
    except KeyboardInterrupt:
        server.server.close()
        print "\nbye!"
    except Exception as e:
        print "error"
        print e
