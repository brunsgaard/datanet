#!/usr/bin/env python

import socket
import select
import logging

class ChatNameServer:

    BUFFERSIZE = 1024
    
    def __init__(self):

        self.input_from = []
        self.names2info = {}
        self.socks2names = {}

        # You should change these settings if not running the service locally
        ns_ip = 'localhost'
        ns_listen_port = 6789

        logging.basicConfig( level=logging.DEBUG
                           , format = '[%(asctime)s] %(levelname)s: %(message)s'
                           )

        self.logger = logging.getLogger('NameServer')

        self.logger.info('Service initialized')

        # Here you should setup the socket needed for listening for incoming
        # peers trying to connect


    def run(self):
        """
        The main loop of the name server
        """
        running = True

        while(running):

            # This is the main loop of the name server
            #
            # This loop needs to:
            # 
            # - Listen for new sockets and create a connection to these
            # - Listen for new request from already connected users
            # - Detect dead sockets and remove these

            pass


    def connect_to_peer(self, sock):
        """
        Establish a connection to a new peer and 
        preform the required handshake
        """

        # You need to setup the connection and preform the handshake here.
        # First you should accept the socket before starting the handshake

        pass


    def parse_request(self, request, sock):
        """
        Parse a request from a peer and preform the appropriate actions
        """
        tokens = request.split()

        if tokens[0] == "USERLIST":
            self.logger.info("User requested userlist")
            self.send_userlist(sock)

        elif tokens[0] == "LOOKUP" and len(tokens) == 1:
            self.logger.info("user requested lookup of user %s" % tokens[1])
            self.lookup_user(tokens[1],sock)

        elif tokens[0] == "LEAVE":
            self.logger.info("User wishes to leave service")
            self.leave_peer(sock)
        else:
            self.logger.info("Unrecognized command '%s' ignored" % request)
            # Remember to send a response indicating bad formating


    def lookup_user(self,nick, sock):
        """
        Lookup a user on the name server
        """
        if nick in self.names2info:
            # Send the appropriate response according to the protocol
            pass
        else:
            # Send the appropriate response according to the protocol
            pass



    def send_userlist(self, sock):
        """
        Send a list of all online users. Response should comply with the protocol
        """
        # Here you should examine the list of connected peers
        # and determine how many peers is connected.
        # You will need to form the responce according to the protocol.
        # Remenber that the user requesting the list shouldn't be on the list.

    def leave_peer(self, sock):
        """
        Close the connection properly to a leaving peer
        """
        # Here you need to send the proper response to the leaving peer
        # and then close the socket and remove the peer from the system
        pass


# Run the server.
if __name__ == "__main__":
    ChatNameServer().run()
