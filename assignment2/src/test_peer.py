#!/usr/bin/env python

from peer import *
import StringIO
import io
import subprocess
import sys
import select
import os

import random
import string

peers = []

ip = "localhost"
port = "6789"

for i in range(10):
    peer = ChatPeer()
    nick = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(5))
    peer.parse_user_request("/nick %s" % nick)
    peer.parse_user_request("/connect %s %s" %(ip, port))

    peers.append(peer)

raw_input("press enter when done")

for peer in peers:
    peer.parse_user_request("/leave")
