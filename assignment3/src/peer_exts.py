# ---------------------------------------------------------------------
# ------------------ NEW METHODS FOR ASSIGNMENT 3 ---------------------
# ---------------------------------------------------------------------
#
# These new methods should be appended to the existing peer.py
# implementation you made last week


    def connect_to_peer(self, user_nick, user_addr):
        """
        Establish a connection to a peer and 
        preform the required handshake
        """
        # Here you should preform the connection to a new peer.
        # You should connect a new socket to the peer and preform the
        # peer-peer handshake.
        pass


    def connect_from_peer(self, sock):
        """
        Accept a connection from a connecting peer
        and preform the required handshake
        """
        # This method is basically the opposite of the above one.
        # Here you need to accept and incoming peer connection
        # and preform the receiver part of the peer-peer handshake.
        pass


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
