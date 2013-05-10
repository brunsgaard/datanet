#!/usr/bin/env python

import socket
import sys
import select
import errno
import os

class ChatPeer:

    BUFFERSIZE = 1024

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

            # This is the main loop of the peer
            #
            # This loop needs to:
            #
            # - Listen for new requests from the user (via stdin)
            # - Detect whether the socket to the name server has died


            # TODO: detect wether the socket has died

            ready_to_read, _, _ = select.select(self.input_from, [], [])

            for inputter in ready_to_read:
                line = file.readline(inputter)

                if not line or line == "\n":
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
        # You need to setup the connection and preform the handshake here.
        # First you should initiate the socket and connect to the name
        # server before starting the handshake

        try:
            ns_port = int(ns_port)
        except ValueError as e:
            print "Port was not an integer"
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
        elif response == "101 TAKEN":
            print "nick already taken"
            self.ns_socket.close()
            self.ns_socket = None
        else:
            # TODO
            print "Strange things happened"
            self.ns_socket.close()
            self.ns_socket = None

    def disconnect_from_ns(self):
        """
        Close the connection properly to the name server
        """
        # Here you should send the appropriate message to the name server
        # letting it know that you are leaving. When getting the correct
        # response your peer should close the socket and set the ns_socket
        # to None.

        self.ns_socket.send("LEAVE")
        response = self.ns_socket.recv(self.BUFFERSIZE)

        if response != "400 BYE":
            print "Unexpected response from server, closing connection:\n%s" % response

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
        # Here you should do a lookup request to the name server on a specific
        # user and return the proper information if that user is connected to
        # the service.
        #
        # Note that this method should not be directly callable for the user.
        # You will need it for the next assignment.

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
        # Here you should make a request to the name server and receive
        # the list of online users from it.
        # You should then format this list and show it to the user.
        # Remember to put the current user on the list as well.

        self.ns_socket.send("USERLIST")

        full_response = self.ns_socket.recv(self.BUFFERSIZE)


        # Hack for knowning we get the whole message.
        # If there's more to be received than the response to this query
        # it will be included in the userlist printing.
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
            print "Unexpected response from server: %s" % response

# Run the server.
if __name__ == "__main__":
    chat_peer = ChatPeer()

    if len(sys.argv) == 2:
        if os.path.isfile(sys.argv[1]):
            chat_peer.input_from.append(open(sys.argv[1],"r"))

    chat_peer.run()
