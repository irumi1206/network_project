import socket
import threading
import sys
import signal

#setting socket
host=sys.argv[1]
port=int(sys.argv[2])
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
client_socket.connect((host,port))

#signal to deal with control c
def control_c(sig,frame):
   print('exit')
   client_socket.close()
   sys.exit(0)
   
signal.signal(signal.SIGINT,control_c)

#input thread
def inp():
   while True:
      message=input()
      print('[You]',message)
      client_socket.send(message.encode())

#output thread     
def out():
   while True:
      in_data=client_socket.recv(1024)
      print(in_data.decode())
      
      
#run input thread and output thread and set it as daemons to terminate when the main thread is shut down     
inp_thr=threading.Thread(target=inp,args=())
out_thr=threading.Thread(target=out,args=())
inp_thr.daemon=True
out_thr.daemon=True
inp_thr.start()
out_thr.start()
inp_thr.join()
out_thr.join()
signal.pause()
