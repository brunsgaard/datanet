#!/usr/bin/env python

"""
A simple echo client
"""

import socket

def help():
        return """
Client usage options:
press Enter or CTRL + c to quit client

other kinds of messages should go to the server
"""

if __name__=='__main__':
  host = 'localhost'
  port = 6789
  size = 1024
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((host,port))
  print help()
  while 1:
    try:
       message = raw_input(">>")
       if message == '':
           print 'closing connection...'
           break
       print 'sent:' , message
       s.send(message)
       data = s.recv(size)
       if not data:
           break
       print "Received:" , data
    except: #catches ANY exception including KeyboardInterrupt .. should use with caution
          print "Client shut down."
          s.close()
          break
  s.close()

