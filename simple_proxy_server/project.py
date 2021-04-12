import os,sys,threading,socket
import signal

port=int(sys.argv[1])
host='127.0.0.1'
proxy_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
proxy_socket.bind((host,port))
proxy_socket.listen()
print("Starting proxy server on port ",port)
num=0
image_flag=False
lock=threading.Lock()
shared_num=0
thr_list=[False for i in range(10000)]

def get_least():
	for i in range(10000):
		if(thr_list[i]==False):
			return i


def control_c(sig,frame):
   print('exit')
   proxy_socket.close()
   sys.exit(0)
   
signal.signal(signal.SIGINT,control_c)



def proxy_threading(conn,client_addr,thrr_num,index):
	global shared_num
	global image_flag
	print_list=[]
	request=conn.recv(999999)
	#length is 0, break
	if(len(request)==0): 
		thr_list[thrr_num]=False;
		return
	request_list=request.split(b'\r\n')
	first_line=request_list[0]
	second_line=request_list[1]
	third_line=request_list[2]
	url=first_line.split()[1].decode('utf-8')
	if(len(url)>=10 and url[-10:]=="?image_off"):
		image_flag=True
	
	elif(len(url)>=9 and url[-9:]=="?image_on"):
		image_flag=False
		
	host_name=second_line.decode('utf-8')[6:]
	user_agent=third_line.decode('utf-8')[12:]
	#if  method connect, break
	method=first_line.split()[0].decode('utf-8')
	if(method=="CONNECT"):
		thr_list[thrr_num]=False;
		conn.close()
		
	redirect_flag=False
	if('yonsei' in url):
		redirect_flag=True
		
		
	#clit-->prx---srv
	print_list.append("------------------------------------------")
	print_list.append(str(index)+" [Conn:"+str(thrr_num+1)+"/"+str(threading.active_count()-1)+"]")
	print_list.append("["+("O" if redirect_flag else "X")+"] URL filter | ["+("O" if image_flag else "X")+"] Image filter")
	print_list.append("[CLI connected to 127.0.0.1:"+str(client_addr[1])+"]")
	print_list.append("[CLI ==> PRX --- SRV]")
	print_list.append(" >"+first_line.decode('utf-8'))
	print_list.append(" >"+user_agent)
	
	
	#iterate request
	if redirect_flag and method=="GET":
		host_name="www.linuxhowtos.org"
		request_list[0]=b"GET http://www.linuxhowtos.org/ HTTP/1.1"
		for i in range(len(request_list)):
			if len(request_list[i])>=8 and request_list[i][:7]==b"Referer":
				request_list[i]=b"Referer: http://www.linuxhowtos.org"
				
			if len(request_list[i])>=5 and request_list[i][:4]==b"Host":
				request_list[i]=b"Host: www.linuxhowtos.org"
		request=b"\r\n".join(request_list)
	
		
		
	
			
	

	
	#cli---prx-->srv
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((host_name,80))
	print_list.append("[SRV connected to "+host_name+"]")
	s.send(request)
	print_list.append("[CLI --- PRX ==> SRV]")
	first_line=request.split(b'\r\n')[0]
	third_line=request.split(b'\r\n')[2]
	host_name=second_line.decode('utf-8')[6:]
	print_list.append(" >"+first_line.decode('utf-8'))
	user_agent=third_line.decode('utf-8')[12:]
	print_list.append(" >"+user_agent)
	
	
	
	
	#cli<--prx<--srv
	while True:
		try:
			data=s.recv(99999)
		except:
			a=1
		if(len(data)>0):
			data_list=data.split(b'\r\n')
			#for the first data
			if(data_list[0][:4]==b"HTTP"):
				status_pos=data_list[0].find(b" ")
				print_list.append("[CLI --- PRX <== SRV]")
				print_list.append(" > "+data_list[0][status_pos+1:].decode('utf-8'))
				flag=False
				for i in data_list:
					if(len(i)>=13 and i[:12]==b"Content-Type"):
						flag=True
						print_list.append(" > "+i[14:].decode('utf-8'))
						if(i[14:19]==b'image' and image_flag ):
							 s.close()
							 conn.close()
							 thr_list[thrr_num]=False
							 return
						for j in data_list:
							if(len(j)>=15 and j[:14]==b"Content-Length"):
								print_list[-1]+=" "
								print_list[-1]+=j[16:].decode('utf-8')
								print_list[-1]+="bytes"
								break
						break
				if(not flag):
					print_list.append(" > ")
				
				print_list.append("[CLI <== PRX --- SRV]")
				print_list.append(print_list[-3])
				print_list.append(print_list[-3])
			
			#send data
			
			
				
			conn.send(data)
		else:
			break
		
			
	#close connection
	s.close()
	conn.close()
	thr_list[thrr_num]=False;
	
	lock.acquire()
	shared_num+=1
	for i in print_list:
		print(i)
	print("[CLI disconnected]")
	print("[SRV disconnected]")
	lock.release()


while True:
	conn,client_addr=proxy_socket.accept()
	num=num+1
	thr_num=get_least()
	thr_list[thr_num]=True
	temp_thr=threading.Thread(target=proxy_threading,args=(conn,client_addr,thr_num,num))
	temp_thr.daemon=True
	temp_thr.start()
	
	
signal.pause()
