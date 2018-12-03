import time
from threading import Thread
from time import sleep
from mlib import SockClient

def io_operation(arg):
	sock = arg
	sleep(0.5)
	
	while True:
		text = input()
		sock.Send(sock._serverStream, text.encode())
		

		
port = 10001               
address = '127.0.0.1'
client = SockClient(address, port)

thread = Thread(target = io_operation, args = (client, ))
thread.start()

while True:
	client.ProcessConnections()
	
	data = client.Receive(client._serverStream, 1024)
	
	if None != data:
		print(str(data.decode()))
	
# close the connection
client.Close()   