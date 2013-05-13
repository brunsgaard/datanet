#!/usr/bin/env python
from socket import *

def help():
        return """
To stop the server:
Linux and Mac: CTRL + c
Windows: CTRL + c or CTRL + d, if it does not work then CTRL + BREAK
"""

if __name__=='__main__':
    HOST = 'localhost'
    PORT = 6789
    BUFSIZ = 1024
    ADDR = (HOST, PORT)
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.bind(ADDR)
    serversock.listen(1)

    while 1:
      try:
        print help()
        print 'waiting for connection...'
        clientsock, addr = serversock.accept()
        print '...connected from:', addr
        while 1:
            data = clientsock.recv(BUFSIZ)
            print 'client sent:' + data
            if not data:
                clientsock.close()
                break
            else:
                clientsock.send("from_server:"+data)
      except: #catches ANY exception including KeyboardInterrupt .. should use with caution
          print "closing server"
          break   
    serversock.close()
                   
        
