import socket
import sys
import readline
import errno

class Client:
    BUFFER_SIZE = 1024
    def __init__(self, port=50000, serverip='localhost'):
        """
        Initialize the variables required by the client
        """
        self.serverip = serverip
        self.port = port

        self.socket = None #use this variable as the client socket

        #Initialize the socket

    def parse_command(self, command):
        """
        Use this method to check that the user input is formatted correctly so that
        only valid requests are sent to the server
        """
        #if ping command
        if command.upper().strip() == '/PING':
            return 'PING'

        #if calc command
        if command[0:6].upper() == '/CALC ':
            pass

        #if echo command
        if len(command) > 6 and command[:6].upper() == '/ECHO ':
            pass

        #return None if the others fail => command not well formed
        return None

    def help(self):
        return """
Client usage options:
/ping
/calc <num1> <operation> <num2>
/echo <text to echo>
/quit or press Enter to quit client

Usage examples:
%/ping
100 PONG ('127.0.0.1', 51758) 10:10:00AM

%/calc 40 + 2
200 EQUALS 42

%/echo Is there anybody out there?
300 Is there anybody out there?
"""

    def run(self):
        """
        The main loop of the server.
        """
        sys.stdout.write(self.help())
        running = True

        #connect the client
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect( (self.serverip, self.port) )

        while running:
            # read from keyboard
            line = raw_input('>')
            line = line.strip()
            # /QUIT does not go to the server , just breaks the loop
            if line.upper() == '/QUIT' or line == '':
                print 'closing connection...'
                self.socket.close()
                break
            request = self.parse_command(line) #parse the user input and check if it is well formed

            if request is not None:#if well formed request
               #Send the request to the server and recevice the response

               # TODO: Sanity check on size
               self.socket.send(request);
               response = self.socket.recv(BUFFER_SIZE)
            else:
               response = 'Unkown command!' + self.help()
            sys.stdout.write(response + '\n')


        #close the socket


        print 'Connection closed. Bye!'


if __name__ == '__main__':
    try:
        Client().run()
    except Exception as e:
        print "error"
        print e

