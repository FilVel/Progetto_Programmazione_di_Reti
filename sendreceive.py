"""
@author: Filippo Velli filippo.velli@studio.unibo.it
"""

import socket as sk
import os
import pathlib as pl

def receive_file(buffer, sock, user):
    data,addr = sock.recvfrom(buffer)
    file_path=pl.PurePath(data.decode()).parts
    if user=='Server':
        data=os.path.join(os.getcwd(), "Server", file_path[-1])
    else:
        data=os.path.join(os.getcwd(), file_path[-1])
    
    f = open(data.strip(),'wb')

    data,addr = sock.recvfrom(buffer)
    try:
        while(data):
            f.write(data)
            sock.settimeout(3)
            data,addr = sock.recvfrom(buffer)
    except sk.timeout:
        sock.settimeout(None)
        f.close()
        if user=='Server':
            return 'File has been uploaded successfully'
        else:
            return 'File has been downloaded successfully'

def send_file(file, addr, sock, buffer, user):
    if user=='Server':
        file = os.path.join(os.getcwd(), "Server", file)
    sock.sendto(file.encode(),addr)
    f=open(file,"rb")
    data = f.read(buffer)
    while (data):
        if(sock.sendto(data,addr)):
             data = f.read(buffer)
    f.close()
    return 'File has been sent successfully'