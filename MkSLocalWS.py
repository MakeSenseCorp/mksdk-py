#!/usr/bin/python
import os
import sys
import json

from collections import OrderedDict
from flask_socketio import SocketIO, emit
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource

if sys.version_info[0] < 3:
	import thread
else:
	import _thread

class MkSLocalWebsocketServer():
	def __init__(self):
		self.ClassName 				= "LocalWebsocketServer"
		self.ApplicationSockets 	= {}
		self.ServerRunning 			= False
		# Events
		self.OnDataArrivedEvent 	= None
		self.OnWSDisconnected 		= None
	
	def AppendSocket(self, ws_id, ws):
		print ("({classname})# Append new connection ({0})".format(ws_id, classname=self.ClassName))
		self.ApplicationSockets[ws_id] = ws
	
	def RemoveSocket(self, ws_id):
		print ("({classname})# Remove connection ({0})".format(ws_id, classname=self.ClassName))
		del self.ApplicationSockets[ws_id]
		if self.OnWSDisconnected is not None:
			self.OnWSDisconnected(ws_id)
	
	def WSDataArrived(self, ws, data):
		# TODO - Append webface type
		packet	= json.loads(data)
		if ("HANDSHAKE" == packet['header']['message_type']):
			return
		
		packet["additional"]["ws_id"] 	= id(ws)
		packet["additional"]["pipe"]  	= "LOCAL_WS"
		packet["stamping"] 				= ['local_ws']
		data = json.dumps(packet)

		if self.OnDataArrivedEvent is not None:
			self.OnDataArrivedEvent(ws, data)
	
	def Send(self, ws_id, data):
		if ws_id in self.ApplicationSockets:
			self.ApplicationSockets[ws_id].send(data)
		else:
			print ("({classname})# ERROR - This socket ({0}) does not exist. (Might be closed)".format(ws_id, classname=self.ClassName))
	
	def IsServerRunnig(self):
		return self.ServerRunning

	def Worker(self):
		try:
			server = WebSocketServer(('', 1982), Resource(OrderedDict([('/', NodeWSApplication)])))

			self.ServerRunning = True
			print ("({classname})# Staring local WS server ...".format(classname=self.ClassName))
			server.serve_forever()
		except Exception as e:
			print ("({classname})# [ERROR] Stoping local WS server ... {0}".format(str(e), classname=self.ClassName))
			self.ServerRunning = False
	
	def RunServer(self):
		if self.ServerRunning is False:
			thread.start_new_thread(self.Worker, ())

WSManager = MkSLocalWebsocketServer()

class NodeWSApplication(WebSocketApplication):
	def __init__(self, *args, **kwargs):
		self.ClassName = "NodeWSApplication"
		super(NodeWSApplication, self).__init__(*args, **kwargs)
	
	def on_open(self):
		print ("({classname})# CONNECTION OPENED".format(classname=self.ClassName))
		WSManager.AppendSocket(id(self.ws), self.ws)

	def on_message(self, message):
		#print ("({classname})# MESSAGE RECIEVED {0} {1}".format(id(self.ws),message,classname=self.ClassName))
		if message is not None:
			WSManager.WSDataArrived(self.ws, message)
		else:
			print ("({classname})# ERROR - Message is not valid".format(classname=self.ClassName))

	def on_close(self, reason):
		print ("({classname})# CONNECTION CLOSED".format(classname=self.ClassName))
		WSManager.RemoveSocket(id(self.ws))