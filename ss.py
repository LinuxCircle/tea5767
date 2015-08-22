'''
    Simple socket server using threads
'''
 
import socket
import sys
import time
 
HOST = ''   # Symbolic name, meaning all available interfaces
PORT = 7878 # Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print ('Socket created')
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
     
print ('Socket bind complete')
 
#Start listening on socket
s.listen(10)
print ('Socket now listening')

def mysend(msg):
        totalsent = 0
        while totalsent < MSGLEN:
            sent = s.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent


 
#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print ('Connected with ' + addr[0] + ':' + str(addr[1]))
    #mysend("gaga".encode('utf-8'))
    i = 0
    while 1:
       s.sendall(str("gagaga").encode("UTF-8"))
       result=conn.recv(1024)
       print(result)  
       time.sleep(1)

s.close()

def mysend(msg):
        totalsent = 0
        while totalsent < MSGLEN:
            sent = s.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
