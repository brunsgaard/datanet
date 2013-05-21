#!/usr/bin/env python

import socket
import select
import logging

class ChatNameServer:

    BUFFERSIZE = 1024
    MAX_NICK_LENGTH = 32

    def __init__(self):

        self.input_from = []
        self.names2info = {}
        self.socks2names = {}

        # these settings should be changed if not running the service locally
        ns_ip = 'localhost'
        ns_listen_port = 6789

        logging.basicConfig( level=logging.DEBUG
                           , format = '[%(asctime)s] %(levelname)s: %(message)s'
                           )

        self.logger = logging.getLogger('NameServer')

        self.logger.info('Service initialized')

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind( (ns_ip, ns_listen_port) )
        self.server.listen(5)


    def run(self):
        """
        The main loop of the name server
        """
        running = True


        while(running):

            # timeout on a minute so we can check for dead sockets ?
            ready_read, _, _ = select.select(self.input_from + [self.server], [], [])

            if self.server in ready_read:
                ready_read.remove(self.server)

                clientsock, addr = self.server.accept()

                self.input_from.append(clientsock)
                self.logger.info( "connection from %s" % str(clientsock.getpeername()) )

            for clientsock in ready_read:
                request = clientsock.recv(self.BUFFERSIZE)
                if not request:
                    self.logger.info( "disconnection from %s" % str(clientsock.getpeername()) )
                    self.close_clientsock(clientsock)
                else:
                    if clientsock not in self.socks2names:
                        self.connect_to_peer(request, clientsock)
                    else:
                        self.parse_request(request, clientsock)


    def connect_to_peer(self, request, sock):
        """
        Establish a connection to a new peer and
        preform the required handshake
        """

        tokens = request.split()

        if len(tokens) != 3 or tokens[0] != "HELLO"\
           or int(tokens[2]) < 1 or int(tokens[2]) > 65535:
            sock.sendall("102 HANDSHAKE EXPECTED")
            self.logger.info("not enough info for handshake %s" % str(sock.getpeername()) )
            self.close_clientsock(sock)
            return

        name = tokens[1]

        if "," in name or self.MAX_NICK_LENGTH < len(name):
            sock.sendall("103 INVALID NICK")
            self.logger.info( "%s invalid nick %s" % (name, sock.getpeername() ) )
            self.close_clientsock(sock)
            return

        if name in self.names2info:
            sock.sendall("101 TAKEN")
            self.logger.info("%s was already taken, disconnecting %s" % (name, sock.getpeername()) )
            self.close_clientsock(sock)
            return

        self.socks2names[sock] = name
        self.names2info[name] = sock.getpeername()[0], int(tokens[2])
        sock.sendall("100 CONNECTED")
        self.logger.info("%s assigned to %s" % (name, sock.getpeername()) )


    def parse_request(self, request, sock):
        """
        Parse a request from a peer and preform the appropriate actions
        """
        tokens = request.split()

        if not tokens:
            sock.sendall("500 BAD FORMAT")
            return

        name = self.socks2names[sock]

        if tokens[0] == "USERLIST":
            self.logger.info("%s requested userlist" % name)
            self.send_userlist(sock)

        elif tokens[0] == "LOOKUP" and len(tokens) == 2:
            self.logger.info("%s requested lookup of user %s" % (name, tokens[1]) )
            self.lookup_user(tokens[1],sock)

        elif tokens[0] == "LEAVE":
            self.logger.info("%s wishes to leave service", name)
            self.leave_peer(sock)
        else:
            self.logger.info("%s Unrecognized command '%s' ignored" % (name, request) )
            sock.sendall("500 BAD FORMAT")


    def lookup_user(self, name, sock):
        """
        Lookup a user on the name server
        """
        if name in self.names2info:
            ip, port = self.names2info[name]
            sock.sendall("200 INFO %s %i" % (ip, port))
        else:
            sock.sendall("201 USER NOT FOUND")


    def send_userlist(self, sock):
        """
        Send a list of all online users. Response should comply with the protocol
        """
        user = self.socks2names[sock]

        if len(self.names2info) == 1:
            sock.sendall("301 ONLY USER")
        else:
            msg = "300 INFO %d " % len(self.names2info)

            infos = []

            for name in self.names2info:
                if name != user:
                    ip, port = self.names2info[name]
                    infos.append("%s %s %s" % (name, ip, port))

            msg += ", ".join(infos)

            print msg

            sock.sendall(msg)



    def leave_peer(self, sock):
        """
        Close the connection properly to a leaving peer
        """

        sock.sendall("400 BYE")
        self.close_clientsock(sock)

    def close_clientsock(self, sock):
        if sock in self.socks2names:
            name = self.socks2names[sock]
            del self.names2info[name]
            del self.socks2names[sock]

            self.logger.info("%s removed from name server" % name)

        sock.close()
        self.input_from.remove(sock)


# Run the server.
if __name__ == "__main__":
    ChatNameServer().run()
