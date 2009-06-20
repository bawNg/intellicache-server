#!/usr/bin/env python

import struct

class IntelliCache_Protocol:
	PROTOCOL_HEADER = 0x0C

	SID_NULL	= 0
	SID_PING	= 1
	SID_LOGIN	= 2

	messageID = { \
		0: "SID_NULL",
		1: "SID_PING",
		2: "SID_LOGIN"
	}

	class CONNECTION_STATUS:
		ERROR		= -1
		CONNECTED	= 0
		LOGGED_IN	= 1
		DISCONNECT	= 2

	class LOGIN_STATUS:
		SUCCESSFUL	= 0
		ERROR		= 1

	def SEND_SID_PING(self):
		pBuilder = self.PacketBuilder(self.SID_PING)
		return pBuilder.raw
	def SEND_SID_LOGIN_RESPONSE(self, status_code, status_message=""):
		pBuilder = self.PacketBuilder(self.SID_LOGIN)
		pBuilder.insertByte(status_code)
		pBuilder.insertNTString(status_message)
		return pBuilder.raw

	class PacketBuilder:
		def __init__(self, packetID=""):
			self.id		= packetID
			self.buffer = []
		def insertData(self, data):
			self.buffer.append(data)
		def insertString(self, data):
			self.buffer.append(data)
		def insertNTString(self, data):
			self.buffer.append(data + chr(0))
		def insertWORD(self, data):
			data = self.makeWORD(data)
			self.buffer.append(data)
		def insertDWORD(self, data):
			data = self.makeDWORD(data)
			self.buffer.append(data)
		def insertQWORD(self, data):
			data = struct.pack('Q', data)
			self.buffer.append(data)
		def insertBytes(self, val1, val2, val3, val4):
			data = struct.pack('BBBB', val1, val2, val3, val4)
			self.buffer.append(data)
		def insertByte(self, val):
			data = struct.pack('B', val)
			self.buffer.append(data)
		def makeDWORD(self, data):
			return struct.pack('I', data)
		def makeWORD(self, data):
			return struct.pack('H', data)
		def clear(self):
			del self.buffer[:]
			self.buffer[:] = []

		def getPacket(self, packetID=""):
			if packetID != "": self.id = packetID
			tmp = ''
			for i in self.buffer: tmp = tmp + i
			packetlen = self.makeWORD(len(tmp) + 4)
			header = chr(IntelliCache_Protocol.PROTOCOL_HEADER) + chr(self.id) + packetlen
			return header + tmp
		raw = property(getPacket)