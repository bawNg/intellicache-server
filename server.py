import logging
import asyncore, socket
import struct, time
from threading import Timer
from packet_handler import IntelliCache_PacketHandler
from util import *
import model as db

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(message)s', datefmt='%H:%M:%S')

class IntelliCache_Server_Connection_Handler(asyncore.dispatcher):
	def __init__(self, sock):
		self.chunk_size = 4096
		self.log = logging.getLogger('[Client Connection] %s' % str(sock.getsockname()))
		asyncore.dispatcher.__init__(self, sock=sock)
		self.recv_buffer = ""
		self.recv_bufLen = 0
		self.write_buffer = []
		self.handler = IntelliCache_PacketHandler(self)
		self.status = self.handler.protocol.CONNECTION_STATUS.CONNECTED
		self.username = ""
		self.handler.SEND_PING_REQUEST()
		
	def writable(self): return bool(self.write_buffer)

	def handle_write(self):
		data = self.write_buffer.pop()
		sent = self.send(data[:self.chunk_size])
		if sent < len(data):
			remaining = data[sent:]
			self.data.to_write.append(remaining)
		#self.log.debug('handle_write() -> (%d)', sent)
		#debugPacket(data[:sent], "Packet contents:")
		if not bool(self.write_buffer):
			if self.status == self.handler.protocol.CONNECTION_STATUS.DISCONNECT:
				self.log.debug("CONNECTION_STATUS: DISCONNECT -- closing connection...")
				self.close()

	def handle_read(self):
		strTemp = self.recv(self.chunk_size)
		self.log.debug("handle_read() -> (%d)" % len(strTemp))
		debugPacket(strTemp, "Packet contents:")
		
		recvLen = len(strTemp)
		if recvLen == 0:
			self.log.debug("Connection lost. (disconnected)")
			self.close()
		
		self.recv_buffer += strTemp
		self.recv_bufLen += recvLen
		
		# Received packet header and length
		while (self.recv_bufLen >= 4):
			# Get packet length
			pktLen, = struct.unpack('H', self.recv_buffer[2:4])
			# Break if received buffer is smaller then packet length
			if (self.recv_bufLen < pktLen):
				print "received buffer is smaller then packet length -- breaking..."
				break
			
			strPacket = self.recv_buffer[:pktLen]
			self.recv_buffer = self.recv_buffer[pktLen:]
			self.recv_bufLen -= pktLen
			
			self.handler.parsePacket(strPacket)

	def handle_close(self):
		self.log.debug('handle_close()')
		self.close()
		
class IntelliCache_Server(asyncore.dispatcher):
	def __init__(self, address):
		self.log = logging.getLogger('[IntelliCache Server]')
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.bind(address)
		self.address = self.socket.getsockname()
		self.log.debug('binding to %s', self.address)
		self.listen(10)

	def handle_accept(self):
		# Called when a client connects to our socket
		client_sock, client_address = self.accept()
		self.log.debug('handle_accept() -> %s', client_address)
		IntelliCache_Server_Connection_Handler(client_sock)	

	def process_forever(self):
		asyncore.loop()
	def handle_close(self):
		self.log.debug('handle_close()')
		self.close()

server = IntelliCache_Server(("", 5500))
server.process_forever()
