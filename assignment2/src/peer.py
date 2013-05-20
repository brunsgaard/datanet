#!/usr/bin/env python

import socket
import sys
import select
import errno
import os

class ChatPeer:

    BUFFERSIZE = 1024
    MAX_NICK_LENGTH = 32

    def __init__(self):

        self.input_from = []
        self.nick = ''
        self.ns_socket = None

        self.input_from.append(sys.stdin)

    def run(self):
        """
        The main loop of the peer
        """

        running = True

        while(running):
            # Print a simple prompt.
            sys.stdout.write('\n> ')
            sys.stdout.flush()

            listeners = self.input_from

            if self.ns_socket:
                listeners = self.input_from + [self.ns_socket]

            ready_read, _, _ = select.select(listeners, [], [])

            if self.ns_socket in ready_read:
                ready_read.remove(self.ns_socket)

                server_msg = self.ns_socket.recv(self.BUFFERSIZE)

                if server_msg:
                    sys.stdout.write("\nserver said: %s\n" % server_msg)
                else:
                    self.ns_socket.close()
                    self.ns_socket = None
                    sys.stdout.write("\nserver closed connection\n")
                sys.stdout.flush()
                continue


            for inputter in ready_read:
                line = file.readline(inputter)

                if not line:
                    self.input_from.remove(inputter)
                    if not self.input_from:
                        print "Shutting down, no more input"
                        self.quit()
                else:
                    if inputter != sys.stdin:
                        sys.stdout.write(line)
                    self.parse_user_request( line.strip() )


    def connect_to_ns(self, ns_ip, ns_port):
        """
        Establish a connection to the name server and
        preform the required handshake
        """

        try:
            ns_port = int(ns_port)
        except ValueError as e:
            print "supplied port was not an integer"
            return

        self.ns_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.ns_socket.connect( (ns_ip, ns_port) )
        except socket.error as msg:
            print "Could not open socket to server"
            self.ns_socket.close()
            self.ns_socket = None
            return

        request = "HELLO %s" % self.nick
        self.ns_socket.send(request)
        response = self.ns_socket.recv(self.BUFFERSIZE)

        if response == "100 CONNECTED":
            print "Connected"
            return

        if response == "101 TAKEN":
            print "nick already taken"
        elif response == "103 INVALID NICK":
            print "server said your nick was invalid"
        else:
            print "Server did not accept nick, responded with: %s\n" % response

        self.ns_socket.close()
        self.ns_socket = None

    def disconnect_from_ns(self):
        """
        Close the connection properly to the name server
        """

        self.ns_socket.send("LEAVE")
        response = self.ns_socket.recv(self.BUFFERSIZE)

        if response != "400 BYE":
            print "Unexpected response from server:%s\n" % response
            print "Closing connection"

        self.ns_socket.close()
        self.ns_socket = None

    def parse_user_request(self, request):
        """
        Parse a request from the user and preform the appropriate actions
        """
        # Please note: in this function we are using the ns_socket to
        # check whether we are connected or not. It is therefor important that
        # the ns_socket is set to None when we don't have a connection.

        tokens = request.split()

        if len(tokens) == 0:
            print "Error: unknown command"
            return

        if tokens[0] == "/connect" and len(tokens) == 3:
            if self.nick == "":
                print "Error: you need to chose a nick name before connecting"
            elif self.ns_socket:
                print "Error: you are already connected to a name server"
            else:
                self.connect_to_ns(tokens[1], tokens[2])

        elif tokens[0] == "/nick" and len(tokens) == 2:
            if ',' in tokens[1]:
                print "Error: can't pick a nick name with ',' in it"
            elif self.MAX_NICK_LENGTH < len(tokens[1]):
                print "Error: nick too long, max %d characters" % self.MAX_NICK_LENGTH
            else:
                self.nick = tokens[1]
                print 'Nick changed to ' + self.nick

        elif tokens[0] == "/userlist":
            if self.ns_socket:
                self.print_users()
            else:
                print "Error: not connected"

        elif tokens[0] == "/lookup" and len(tokens) == 2:
            if self.ns_socket:
                self.lookup_peer(tokens[1])
            else:
                print "Error: not connected"

        elif tokens[0] == "/leave":
            if self.ns_socket:
                self.disconnect_from_ns()
                print "Left Name Server"
            else:
                print "Error: not connected"

        elif tokens[0] == "/quit":
            print "Shutting down"
            self.quit()
        else:
            print "Error: unknown command"


    def quit(self):
        """
        Quit and close sockets / file streams
        """

        if self.ns_socket:
            self.disconnect_from_ns()

        for inputter in self.input_from:
            inputter.close()

        sys.exit(0)

    def lookup_peer(self, user):
        """
        Query the name server for information on a user by it's nick
        """

        request = "LOOKUP %s" % user
        self.ns_socket.send(request)
        response = self.ns_socket.recv(self.BUFFERSIZE)

        tokens = response.split()

        if tokens[0] == "200" and len(tokens) == 3:
            print "user found at ip: %s" % tokens[2]
        elif tokens[0] == "201":
            print "user not found"
        else:
            print "Unexpected response from server: %s" % response


    def print_users(self):
        """
        Get the list of online users and print it using nice formating
        """

        self.ns_socket.send("USERLIST")

        full_response = self.ns_socket.recv(self.BUFFERSIZE)


        # Hack for receiving the whole message.
        # If there's more messages to be received than the userlist message,
        # it will be also be printed now :(
        self.ns_socket.setblocking(0)
        while True:
            try:
                response = self.ns_socket.recv(self.BUFFERSIZE)
                full_response += response
            except socket.error as e:
                break
        self.ns_socket.setblocking(1)

        tokens = full_response.split()

        if tokens[0] == "300":
            print "%s - You" % self.nick

            users = " ".join(tokens[3:]).split(",")

            for user in users:
                print " - ".join( user.strip().split() )

        elif tokens[0] == "301":
            print "%s - You" % self.nick
        else:
            print "Unexpected response from server: %s" % full_response

# Run the server.
if __name__ == "__main__":
    chat_peer = ChatPeer()

    if len(sys.argv) == 2:
        if os.path.isfile(sys.argv[1]):
            chat_peer.input_from.append(open(sys.argv[1],"r"))

    chat_peer.run()
