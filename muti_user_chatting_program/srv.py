import socket
import threading
import sys
import signal

#setting for socket
host=sys.argv[1]
port=int(sys.argv[2])
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host,port)) 
server_socket.listen()
client_num=0
client_socket_list=[]
exist_list=[]

#handling control c interruption
def control_c(sig,frame):
   print('exit')
   server_socket.close()
   sys.exit(0)
   
signal.signal(signal.SIGINT,control_c)

#returns activating ser_threading
def current_alive():
   global exist_list
   num=0
   for idx in range(len(exist_list)):
   	if exist_list[idx]!=0:
   		num=num+1
   		
   if num>1: return str(str(num)+' users')
   else: return str(str(num)+' user')
   
#thread to deal with each client_socket
def server_threading(client_socket,addr,index):
   #prints the current client, send current client connected, and send connection message to other clients
   print('> New user %s:%d entered (%s online)'%(addr[0],addr[1],current_alive()))
   start_msg='> Connected to the chat server ('+str(current_alive())+' online)'
   client_socket.send(start_msg.encode())
   
   for idx in range(len(client_socket_list)):
      if exist_list[idx]!=0 and idx!=index:
         data1='> New user '+addr[0]+':'+str(addr[1])+' entered ('+str(current_alive())+' online)'
         client_socket_list[idx].send(data1.encode())
   #waits for data from the socket
   while True:
      try:
         data=client_socket.recv(1024)
         #if client_socket is closed, it sends empty data
         if not data:
            break
         print('[%s:%d]'%(addr[0],addr[1]),data.decode())
         for idx in range(len(client_socket_list)):
            if exist_list[idx]!=0 and idx!=index:
               msg_to_client='['+addr[0]+':'+str(addr[1])+'] '+data.decode()
               client_socket_list[idx].send(msg_to_client.encode())
      except:
         break
   #if the connection is closed, send the disconnection message to other clients
   exist_list[index]=0
   print('< The user %s:%d left (%s online)'%(addr[0],addr[1],current_alive()))
   for idx in range(len(client_socket_list)):
      if exist_list[idx]!=0:
         data2='< The user '+addr[0]+':'+str(addr[1])+' left ('+str(current_alive())+' online)'
         client_socket_list[idx].send(data2.encode())
   client_socket.close()
   

print('Chat Server started on port %d.'%(port))
while True:
   #for every client connecttion, run th server_threading
   client_socket,addr=server_socket.accept()
   new_client=threading.Thread(target=server_threading,args=(client_socket,addr,client_num))
   new_client.daemon=True
   client_num=client_num+1
   client_socket_list.append(client_socket)
   exist_list.append(1)
   new_client.start()
#for interruption
signal.pause()

