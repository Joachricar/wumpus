#!/usr/bin/python           # This is server.py file

import socket               # Import socket module
import threading
import datetime

class Message():
	def __init__(self, connection, message):
		self.connection = connection
		self.message = message
	def reply(self, message):
		self.connection.senf(message)
		self.connection.close()

queue = []
class WHServer(threading.Thread):
  	def run(self):
  		global queue
		s = socket.socket()
		host = socket.gethostname()
		port = 12345
		s.bind((host, port))
		s.listen(5)
		while True:
		   	c, addr = s.accept()
		   	msg = c.recv(1024)
		   	c.send("LOL")
		   	queue.append(Message(c, msg))

serv = WHServer()
serv.start()

print "Server running"

def event():
	if not queue:
		return
	for e in queue:
		print "elns"
		reply = board.update(e.message)
		e.reply(reply)

while True:
	event()
