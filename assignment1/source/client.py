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
            return "CALC " + command[6:]

        #if echo command
        if len(command) > 6 and command[:6].upper() == '/ECHO ':
            return "ECHO " + command[6:]

        #return None if the others fail => command not well formed
        return None

    def help(self):
        return """
Client usage options:
/help to print this message
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
        #connect the client
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            print "Could not create socket"
            self.socket = None
            return
        try:
            self.socket.connect( (self.serverip, self.port) )
        except socket.error as msg:
            print "Could not open socket to server"
            self.socket.close()
            self.socket = None
            return

        sys.stdout.write(self.help())
        running = True

        while running:
            # read from keyboard
            line = raw_input('>')
            line = line.strip()
            # /QUIT does not go to the server , just breaks the loop
            if line.upper() == '/QUIT' or line == '':
                print 'closing connection...'
                break
            request = self.parse_command(line) #parse the user input and check if it is well formed

            if request is not None: #if well formed request
                if len(request) <= self.BUFFER_SIZE:
                    self.socket.send(request);
                    response = self.socket.recv(self.BUFFER_SIZE)

                    if not response:
                        print 'server did not respond, closing connection...'
                        break
                else:
                    response = "Too large command, max %d chars" % self.BUFFER_SIZE

            elif line.upper() == '/HELP':
                response = self.help()
            else:
               response = 'Unkown command! use /help to see valid commands'
            sys.stdout.write(response + '\n')

        self.socket.close()
        print 'Connection closed. Bye!'


if __name__ == '__main__':
    try:
        Client().run()
    except Exception as e:
        print "error"
        print e
