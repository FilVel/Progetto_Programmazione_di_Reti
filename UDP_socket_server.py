"""
@author: Filippo Velli filippo.velli@studio.unibo.it
"""

import socket as sk
import time
import os
import sys
import pathlib as pl
import sendreceive as sr

#List of the available options that will be sent to the client
messages=[' list:   Show you the list of files on the server',
          ' get:    Let you download a file from the server',
          ' put:    Let you upload a file to the server',
          ' bye:    Close the connection']

intro='\r\n Welcome to the DUServer\r\n What can I do for you?\r\n Write the first word to use the command'
default_message=os.linesep.join(messages)
mistake=' Something went wrong! Try again! PS. Choose one of the available options'
nodirectory='The Server subfolder has been deleted. Create another one'
nofiles='No files are present in the Server folder. Add some before using this application'

#Function used to build the list of available files on the server
def build_list():
    filelist=os.listdir('Server')
    filelist=os.linesep.join(filelist)
    return filelist

#Function used to check whether a file exists in the server (get) or a file
#by the same name and extension exists already on the server (put). In both
#case scenarios the function also checks if the file involved is empty or not
def check_file_status(file, request):
    filelist=os.listdir('Server')
    directory = os.path.join(os.getcwd(), "Server", file)
    if request=='get':
        if file not in filelist:
            return 'That file does not exist on the Server'
        elif os.stat(directory).st_size == 0:
            return 'The file you asked for is empty'
        else: 
            return 'success'
    elif request=='put':
        file_path=pl.PurePath(file).parts
        file_name=file_path[-1]
        if file_name in filelist:
            return 'File already present on the Server'
        else:
            return 'success'

def preliminary_check():
    directory = os.path.join(os.getcwd(), "Server")
    #Checking whether the subfolder Server exists, if it does not the this
    #file's execution will cease immediately
    if pl.Path(directory).is_dir()!=True:
        return nodirectory
    filelist=os.listdir('Server')
    #Similar to the previous one, but this instead checks whether the subfolder
    #does at least contain a file, if it does not the execution is immediately
    #interrupted
    if len(filelist)==0:
        return nofiles
    else:
        return 'success'

user='Server'
status=preliminary_check()
if status!='success':
    print(status)
    time.sleep(5)
    sys.exit()

#Socket creation
sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

#Binding server's address
server_address = ('localhost',10000)
print('\r\n starting up on %s port %s'% server_address)
sock.bind(server_address)

while True:
    data, address = sock.recvfrom(4096)
    print(data.decode('utf8'))
    time.sleep(2)
    sent = sock.sendto(intro.encode(), address)
    while True:
        filelist=build_list()
        sent = sock.sendto(default_message.encode(), address)
        data, address = sock.recvfrom(4096)
            
        print('received request')
        request=data.decode('utf8')
        print(request)
        time.sleep(2)
        status=preliminary_check()
        if status!='success':
            print(status)
            status+='\r\n Goodbye'
            sent = sock.sendto(status.encode(), address)
            time.sleep(5)
            sock.close()
            sys.exit()
        if request=='list':
            #Makes a list of the available files and sends it to the client
            filelist=build_list()
            sent = sock.sendto(filelist.encode(), address)
        elif request=='get' or request=='put': 
            #Lets a user download/upload a file from/to the server
            if request=='get':
                sent = sock.sendto('which file? (name+extension)'.encode(), address)
            else:
                sent = sock.sendto('which file? (use its absolute path)'.encode(), address)
            data, address = sock.recvfrom(4096)
            file=data.decode('utf8')
            #When file is 'error' it means that the client tried to upload
            #a file that does not exist or taht is empty. If it is not 'error'
            #normal execution takes place
            if file!='error':
                status=check_file_status(file,request)
                print(status)
                time.sleep(2)
                sent = sock.sendto(status.encode(), address)
                if(status=='success'):
                    if request=='get':
                        outcome=sr.send_file(file, address, sock, 4096, user)
                        success_status, address = sock.recvfrom(4096)
                        print(' CLIENT: %s' %success_status.decode('utf8'))
                    else:
                        outcome=sr.receive_file(4096, sock, user)
                    print(' SERVER: %s' %outcome)
                    time.sleep(2)
                    sent = sock.sendto(outcome.encode(), address) 
        elif request=='bye':
            #Interruption of the comunications between the server and the
            #current client
            sent = sock.sendto('Goodbye'.encode(), address)
            break
        else:
            sent = sock.sendto(mistake.encode(), address)
            
        time.sleep(2)
        print('sent %s back to %s' % (sent,address))
    print('waiting for new client')
