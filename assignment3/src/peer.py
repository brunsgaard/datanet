#!/usr/bin/env python

import socket
import sys
from select import select
import errno
import os
import random


class ChatPeer:

    BUFFERSIZE = 1024
    MAX_NICK_LENGTH = 32

    def __init__(self):

        self.s = dict()
        self.s['listening'] = self.setup_listening_socket()
        self.s['ns'] = None

    def run(self):

        while(True):
            # Print a simple prompt.
            sys.stdout.write('\n> ')
            sys.stdout.flush()

            ready_read, _, _ = select(filter(None, self.s.values())
                                      + [sys.stdin], [], [])

            for o in ready_read:

                if isinstance(o, socket.socket):

                    if o is self.s['ns']:
                        self.read_from_ns_socket()

                    elif o is self.s['listening']:
                        self.connect_from_peer(o.accept()[0])
                    else:
                        d =  o.recv(1024)
                        if not d:
                            o.close()
                            del self.s[o]


                else:
                    self.parse_user_request(sys.stdin.readline())

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

        self.s['ns'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s['ns'].connect( (ns_ip, ns_port) )
        except socket.error as msg:
            print "Could not open socket to server"
            self.s['ns'].close()
            self.s['ns'] = None
            return

        request = "HELLO %s %i" % (self.nick,
                                   self.s['listening'].getsockname()[1])
        self.s['ns'].send(request)
        response = self.s['ns'].recv(self.BUFFERSIZE)

        if response == "100 CONNECTED":
            print "Connected"
            return

        if response == "101 TAKEN":
            print "nick already taken"
        elif response == "103 INVALID NICK":
            print "server said your nick was invalid"
        else:
            print "Server did not accept nick, responded with: %s\n" % response

        self.s['ns'].close()
        self.s['ns'] = None

    def disconnect_from_ns(self):
        """
        Close the connection properly to the name server
        """

        self.s['ns'].send("LEAVE")
        response = self.s['ns'].recv(self.BUFFERSIZE)

        if response != "400 BYE":
            print "Unexpected response from server:%s\n" % response
            print "Closing connection"

        self.s['ns'].close()

    def read_from_ns_socket(self):
        server_msg = self.s['ns'].recv(self.BUFFERSIZE)
        if server_msg:
            sys.stdout.write("\nserver said: %s\n" % server_msg)
        else:
            self.s['ns'].close()
            sys.stdout.write("\nserver closed connection\n")
        sys.stdout.flush()

    def parse_user_request(self, request):
        """
        Parse a request from the user and preform the appropriate actions
        """
        # Please note: in this function we are using the ns_socket to
        # check whether we are connected or not. It is therefor important that
        # the ns_socket is set to None when we don't have a connection.

        if not request:
            print "Shutting down, no more input"
            self.quit()
            return

        tokens = request.strip().split()

        if len(tokens) == 0:
            print "Error: unknown command"
            return

        if tokens[0] == "/connect" and len(tokens) == 3:
            if getattr(self, self.nick, None):
                print "Error: you need to chose a nick name before connecting"
            elif self.s['ns']:
                print "Error: you are already connected to a name server"
            else:
                self.connect_to_ns(tokens[1], tokens[2])

        elif tokens[0] == "/msg" and len(tokens) == 3:
            receiver = tokens[1]

            if receiver not in self.s:
                kwargs = self.lookup_peer(receiver)
                self.connect_to_peer(**kwargs)

            self.s[receiver].send(' '.join(tokens[2:]))

        elif tokens[0] == "/nick" and len(tokens) == 2:
            if ',' in tokens[1]:
                print "Error: can't pick a nick name with ',' in it"
            elif self.MAX_NICK_LENGTH < len(tokens[1]):
                print "Error: nick too long, max %d characters" %\
                    self.MAX_NICK_LENGTH
            else:
                self.nick = tokens[1]
                print 'Nick changed to ' + self.nick

        elif tokens[0] == "/userlist":
            if self.s['ns']:
                self.print_users()
            else:
                print "Error: not connected"

        elif tokens[0] == "/lookup" and len(tokens) == 2:
            if self.s['ns']:
                print self.lookup_peer(tokens[1]).get('msg')
            else:
                print "Error: not connected"

        elif tokens[0] == "/leave":
            if self.s['ns']:
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

        if self.s['ns']:
            self.disconnect_from_ns()

        for s in filter(None, self.s.values()):
            s.close()

        sys.exit(0)

    def lookup_peer(self, user, **kwargs):
        """
        Query the name server for information on a user by it's nick
        """

        request = "LOOKUP %s" % user
        self.s['ns'].send(request)
        response = self.s['ns'].recv(self.BUFFERSIZE)

        tokens = response.split()

        kwargs['status_code'] = int(tokens[0])
        kwargs['nick'] = user

        if tokens[0] == "200" and len(tokens) == 4:
            kwargs['ip'] = tokens[2]
            kwargs['port'] = int(tokens[3])
            kwargs['msg'] = "User found at ip: %s %s" % (tokens[2], tokens[3])

        elif tokens[0] == "201":
            kwargs['msg'] = "User not found"

        else:
            kwargs['msg'] = "Unexpected response from server: %s" % response

        return kwargs


    def print_users(self):
        """
        Get the list of online users and print it using nice formating
        """

        self.s['ns'].send("USERLIST")

        full_response = self.s['ns'].recv(self.BUFFERSIZE)


        # Hack for receiving the whole message.
        # If there's more messages to be received than the userlist message,
        # it will be also be printed now :(
        self.s['ns'].setblocking(0)
        while True:
            try:
                response = self.s['ns'].recv(self.BUFFERSIZE)
                full_response += response
            except socket.error as e:
                break
        self.s['ns'].setblocking(1)

        tokens = full_response.split()
        print tokens

        if tokens[0] == "300":
            print "%s - You" % self.nick

            users = " ".join(tokens[3:]).split(",")

            for user in users:
                print " - ".join( user.strip().split() )

        elif tokens[0] == "301":
            print "%s - You" % self.nick
        else:
            print "Unexpected response from server: %s" % full_response

    def connect_to_peer(self, **kwargs):
        """
        Establish a connection to a peer and
        preform the required handshake
        """
        # Here you should preform the connection to a new peer.
        # You should connect a new socket to the peer and preform the
        # peer-peer handshake.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print kwargs
            s.connect(('localhost', kwargs['port']))
        except socket.error as e:
            print "Could not open socket to server"
            raise e
            s.close()
            return

        request = "HELLO %s" % kwargs['nick']

        s.send(request)
        response = s.recv(self.BUFFERSIZE)

        if response == "100 CONNECTED":
            self.s[kwargs['nick']] = s
            print "Connected"
            return

        if response == "101 REFUSED":
            print "Peer said that nick was already taken"
        elif response == "102 HANDSHAKE EXPECTED":
            print "Peer said your nick was invalid"
        else:
            print "Peer responded with: %s\n" % response

        s.close()

    def connect_from_peer(self, sock):
        """
        Accept a connection from a connecting peer
        and preform the required handshake
        """
        #msg = sock.recv(self.BUFFERSIZE)
        print "connect from peer"

        print 'handshake'

        handshake = sock.recv(1024)
        tokens = handshake.split()

        if handshake.startswith('HELLO'):
            if len(tokens) < 2:
                sock.send('102 HANDSHAKE EXPECTED')
            else:
                if ' '.join(tokens[1:]) in self.s:
                    sock.send('101 REFUSED')
                else:
                    self.s[' '.join(tokens[1:])] = sock
                    sock.send('100 CONNECTED')
                    return
        else:
            sock.send('BAD FORMAT')

        sock.close()

        # This method is basically the opposite of the above one.
        # Here you need to accept and incoming peer connection
        # and preform the receiver part of the peer-peer handshake.


    def parse_peer_request(self, request, sock):
        """
        Parse a request from a connected peer and preform the appropriate actions
        """
        parts = request.split()

        if len(parts) > 0 and parts[0] == "MSG":
            # Do the appropriate actions according to the protocol.
            pass
        elif len(parts) > 0 and parts[0] == "LEAVE":
            # Do the appropriate actions according to the protocol.
            pass
        else:
            print "Unrecognized command '%s' from peer %s ignored" % \
                (data, self.socks2nicks[sock])
            # Remember to send a response indicating bad formating


    def disconnect_from_peers(self):
        """
        Close the connection properly to all connected peers
        """
        # Here you should close the connection to all peers
        # that are currently connected.
        # Remember to send the appropriate leave requests.
        pass

    def send_message(self, user, msg):
        """
        Send a message to a peer that is already connected to
        """
        # Here you should send a message to a connected peer.
        # Remember to check if you receive a message ack.
        pass

    def broadcast(self, msg):
        """
        Broadcast a message to all users in the system. Establishing
        connections to peers is also a part of this function.
        """
        # Here you should first make sure that you have established a
        # connection to all peers on the system.
        # When these connections are obtained, you should send the message
        # to every peer like you would send a regular message.
        pass

    def setup_listening_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        ports = range(50000, 60000)
        random.shuffle(ports)

        for port in ports:
            try:
                s.bind(('localhost', port))
                print 'listen on port %i' % port
                break
            except socket.error as ex:
                if ex.errno == errno.EADDRINUSE:
                    continue
                break
        s.listen(5)
        return s


# Run the server.
if __name__ == "__main__":
    chat_peer = ChatPeer()

    if len(sys.argv) == 2:
        if os.path.isfile(sys.argv[1]):
            chat_peer.input_from.append(open(sys.argv[1],"r"))

    chat_peer.run()
