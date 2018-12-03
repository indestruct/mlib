import socket
import select

class SimpleStream:
	def __init__(self, socketStream, socketAddress):
		self._socketStream = socketStream
		self._socketAddress = socketAddress
		
	def GetSocketStream(self):
		return self._socketStream
		
	def GetSocketAddress(self):
		return self._socketAddress
		
	def Send(self, data):
		isSent = True
		
		dataSent = 0
		while dataSent < len(data):
			sent = self._socketStream.send(data[dataSent:])
			if sent == 0:
				isSent = False

			dataSent = dataSent + sent
		
		return isSent
		
	def Receive(self, len):
		return self._socketStream.recv(len)

class SimpleSocket:
	_NONBLOCKING = 0
	_address     = ''
	_port        = 0
	_type        = socket.SOCK_STREAM
	_mode        = 0

	def __init__(self, address = '', port = 0, type = 0, mode = 0):
		self._address = address
		self._port = port
		# TODO: Set the type of the socket
		# TODO: Set the mode of the socket
		
		# Create an INET socket instance
		self._socket = socket.socket(socket.AF_INET, self._type)
		
		# Set the socket options
		# Currently supporting only non blocking socket implementation
		if self._NONBLOCKING == self._mode:
			self._socket.setblocking(0)
		
	
	def GetSocket(self):
		return self._socket
	
	def Bind(self):
		# Bind the socket to the given address and port
		self._socket.bind((self._address, self._port))
		
	def Listen(self, connections):
		self._socket.listen(connections)
		
	def Accept(self):
		(clientsocket, address) = self._socket.accept()
		newStream = SimpleStream(clientsocket, address)
		return newStream		
	
	def Connect(self):
		self._socket.connect_ex((self._address, self._port))
	
	def Close(self):
		self._socket.close()
		
class Sockserver:
	_NONBLOCKING = 0
	_RECEIVE_BUFFER = 1024
	_BLOCKING = 1
	_MAX_CONNECTIONS = 20

	def __init__(self, address = '', port = 0, mode = 0):
		self._address = address
		self._port = port
		self._clientStreamList = []
		self._onConnectionCb = None
		
		# TODO: Type and mode not supported
		self._simpleSock = SimpleSocket(address, port)
		
		# Bind the socket to the given address and port
		self._simpleSock.Bind()
		
	def Listen(self, connections = _MAX_CONNECTIONS):
		self._simpleSock.Listen(connections)
	
	def Accept(self):
		"""
			Note that this function call will block only if at 
			initialization the mode is set to BLOCKING.
		"""	
		# Accept connections from the socket
		stream = self._simpleSock.Accept()
		self._clientStreamList.append(stream)
		
		if None != self._onConnectionCb:
			self._onConnectionCb(stream)
		
	def Send(self, stream, data):
		potential_readers = []
		potential_writers = []
		potential_errors = []
		
		potential_writers.append(stream.GetSocketStream())
		ready_to_read, ready_to_write, in_error = select.select(potential_readers, potential_writers, potential_errors, 1)
		
		for writers in ready_to_write:
			isSent = stream.Send(data)

	def Receive(self, stream, len):
		potential_readers = []
		potential_writers = []
		potential_errors = []
		
		potential_readers.append(stream.GetSocketStream())
		ready_to_read, ready_to_write, in_error = select.select(potential_readers, potential_writers, potential_errors, 1)
		
		for readers in ready_to_read:
			return stream.Receive(len)
		
	
	def ProcessConnections(self, timeout):
		potential_readers = []
		potential_writers = []
		potential_errors = []
		
		potential_readers.append(self._simpleSock.GetSocket())
		ready_to_read, ready_to_write, in_error = select.select(potential_readers, potential_writers, potential_errors, timeout)
		
		for sock in ready_to_read:
			self.Accept()
	
	def ProcessAll(self, timeout):
		potential_readers = []
		potential_writers = []
		potential_errors = []
		
		potential_readers.append(self._simpleSock.GetSocket())
		for stream in self._clientStreamList:
			potential_readers.append(stream.GetSocketStream())
		
		ready_to_read, ready_to_write, in_error = select.select(potential_readers, potential_writers, potential_errors, timeout)
		
		for sock in ready_to_read:
			if sock == self._simpleSock.GetSocket():
				self.Accept()
			else:
				data = self.Receive(stream, 1024)
				file = open("output.txt", "a")
				file.write(str(data.decode())) 
				file.close() 
	
	def Close(self):
		self._simpleSock.Close()

	def SetOnConnectionCb(self, cb):
		self._onConnectionCb = cb
		
class SockClient:
	_NONBLOCKING = 0
	_RECEIVE_BUFFER = 1024
	_BLOCKING = 1
	
	def __init__(self, address = '', port = 0, mode = 0):
		self._address = address
		self._port = port
		self._serverStream = None
		self._connected = False
		self._onConnectionCb = None
		
		# TODO: Type and mode not supported
		self._simpleSock = SimpleSocket(address, port)

	def Connect(self):
		self._simpleSock.Connect()
		
	def Send(self, stream, data):
		potential_readers = []
		potential_writers = []
		potential_errors = []
		
		potential_writers.append(stream.GetSocketStream())
		ready_to_read, ready_to_write, in_error = select.select(potential_readers, potential_writers, potential_errors, 1)
		
		for writers in ready_to_write:
			isSent = stream.Send(data)

		return isSent
			
	def Receive(self, stream, len):
		potential_readers = []
		potential_writers = []
		potential_errors = []
		
		potential_readers.append(stream.GetSocketStream())
		ready_to_read, ready_to_write, in_error = select.select(potential_readers, potential_writers, potential_errors, 1)
		
		for readers in ready_to_read:
			return stream.Receive(len)
		
		return None
		
	def ProcessConnections(self):
		if self._connected == False:
			self.Connect()
			potential_readers = []
			potential_writers = []
			potential_errors = []
			potential_writers.append(self._simpleSock.GetSocket())
			ready_to_read, ready_to_write, in_error = select.select(potential_readers, potential_writers, potential_errors, 1)
			
			if len(ready_to_write) != 0:
				self._connected = True
				self._serverStream = SimpleStream(self._simpleSock.GetSocket(), self._address)
				if None != self._onConnectionCb:
					self._onConnectionCb(self._serverStream)
				
	def IsConnected(self):
		return self._connected
		
	def GetServerStream(self):
		return self._serverStream
		
	def Close(self):
		self._simpleSock.Close()

	def SetOnConnectionCb(self, cb):
		self._onConnectionCb = cb