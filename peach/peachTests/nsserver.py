#!/usr/bin/env python2

# Echo server program
import socket
import random
import time

HOST = ''                 # Symbolic name meaning the local host
PORT = 50008              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(2)
while True:
    conn, addr = s.accept()
    print 'Connected by', addr
    ready = True
    #data = conn.recv(1)
    while ready:
        if random.randint(0,2) > 0:
            print('sent opt1')
            conn.send('opt1.1opt1.2')
        elif random.randint(0,2) > 0:
            print('sent opt2')
            conn.send('opt2.1opt2.2opt2.3')
        else:
            print('break')
            conn.send('abexit')
        data = conn.recv(2**16)
        print('Received',data)
        if 'finally' in data or data == '':
            ready = False
            conn.close()
        else:
            pass
            #time.sleep(2)
