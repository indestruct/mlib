from mlib import Sockserver
	
class chatClient:
	def __init__(self, stream):
		self._name = ""
		self._hasName = False
		self._stream = stream
		
	def GetName(self):
		return self._name
		
	def SetName(self, name):
		self._name = name
		self._hasName = True
	
	def HasName(self):
		return self._hasName
	
	def GetStream(self):
		return self._stream
		
port = 10001               
address = '127.0.0.1'
server = Sockserver(address, port)
serverName = "The chat room"
clientsList = []


def clientConnectedCb(stream):
	newClient = chatClient(stream)
	clientsList.append(newClient)
	data_out = "Welcome to " + serverName + "! Please enter your name"
	server.Send(newClient.GetStream(), data_out.encode())
	
server.SetOnConnectionCb(clientConnectedCb)
server.Listen(2)



# a forever loop until we interrupt it or 
# an error occurs
while True:
	#while True:
	#	server.ProcessAll(0.5)
	server.ProcessConnections(0.5)
	
	for client in clientsList:
		
		#send periodically data to everyone
		data = server.Receive(client.GetStream(), 1024)
		if None != data:
			if False == client.HasName():
				client.SetName(str(data.decode()))
				data_out = client.GetName() + ", welcome to " + serverName + "!"
				server.Send(client.GetStream(), data_out.encode())
				
				for client_out in clientsList:
					if client.GetStream() != client_out.GetStream():
						data_out = client.GetName() + " has joined the room."
						server.Send(client_out.GetStream(), data_out.encode())
			else:
				for client_out in clientsList:
					if client.GetStream() != client_out.GetStream():
						data_out = client.GetName() + ": " + data.decode()
						server.Send(client_out.GetStream(), data_out.encode())
						
			file = open("log.txt", "a")
			file.write(str(data.decode())) 
			file.close() 
			