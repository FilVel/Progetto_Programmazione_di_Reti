"""
@author: Filippo Velli filippo.velli@studio.unibo.it
"""

import socket as sk
import time
import os
import pathlib as pl
import sendreceive as sr

error='That file does not exist'
file_empty='The file you want to upload is empty'

user='Client'

#Socket creation
sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

#Binding server's address
server_address = ('localhost',10000)
request='Hello'
print('sending %s' % request)
sent = sock.sendto(request.encode(), server_address)
print('waiting to receive')
data, server = sock.recvfrom(4096)
print('%s' %data.decode('utf8'))

try:
    while True:
        data, server = sock.recvfrom(4096)
        print('%s' %data.decode('utf8'))
        request=input(' your command... ')
        print(' sending %s' % request)
        time.sleep(2)
        sent = sock.sendto(request.encode(), server_address)
        print(' waiting to receive ')
        data, server = sock.recvfrom(4096)
        if 'which file?' in data.decode('utf8'):
            filename=input(' %s\n' %data.decode('utf8'))
            time.sleep(2)
            #If the client wants to upload a file (put) that doesn't exist or
            #that is empty, the procedure will be immediately interrupted
            if request!='get' and pl.Path(filename).is_file()!=True:
                print(error)
                sent = sock.sendto('error'.encode(), server_address)
            elif request!='get' and os.stat(filename).st_size == 0:
                print(file_empty)
                sent = sock.sendto('error'.encode(), server_address)
            else:
                sent = sock.sendto(filename.encode(), server_address)
                status, server = sock.recvfrom(4096)
                if(status.decode('utf8')!='success'):
                    print(status.decode('utf8'))
                else:
                    if request=='get':
                        outcome = sr.receive_file(4096, sock, user)
                        time.sleep(2)
                        sent = sock.sendto(outcome.encode(), server_address)
                    else:
                        outcome = sr.send_file(filename, server, sock, 4096, user)
                    print(' CLIENT: %s' %outcome)
                    success_status, address = sock.recvfrom(4096)
                    print(' SERVER: %s' %success_status.decode('utf8'))
        elif 'Goodbye' in data.decode('utf8'):
            print(data.decode('utf8'))
            break
        #This clause occurs only if the request is list or a request
        #is made to the server that the latter can not satisfy
        else:
            print(' %s\r\n' %data.decode('utf8'))
except Exception as info:
    print(info)
finally:
    print(' closing socket')
    sock.close()
