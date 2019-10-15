#!/usr/bin/python
import os
import urllib2
import urllib
import websocket
import sys
if sys.version_info[0] < 3:
	import thread
else:
	import _thread
import time
import json

from mksdk import MkSBasicNetworkProtocol

class Network ():
	def __init__(self, uri, wsuri):
		self.Name 		  	= "Communication to Node.JS"
		self.BasicProtocol 	= None
		self.ServerUri 	  	= uri
		self.WSServerUri  	= wsuri
		self.UserName 	  	= ""
		self.Password 	  	= ""
		self.UserDevKey   	= ""
		self.WSConnection 	= None
		self.DeviceUUID   	= ""
		self.Type 		  	= 0
		self.State 			= "DISCONN"

		self.OnConnectionCallback 		= None
		self.OnDataArrivedCallback 		= None
		self.OnErrorCallback 			= None
		self.OnConnectionClosedCallback = None

	def GetNetworkState(self):
		return self.State

	def GetRequest (self, url):
		try:
			req = urllib2.urlopen(url, timeout=1)
			if req != None:
				data = req.read()
			else:
				return "failed"
		except:
			return "failed"

		return data
		
	def PostRequset (self, url, payload):
		try:
			data = urllib2.urlopen(url, payload).read()
		except:
			return "failed"
		
		return data

	def Authenticate (self, username, password):
		print ("[DEBUG::Network] Authenticate")
		data = self.GetRequest(self.ServerUri + "fastlogin/" + self.UserName + "/" + self.Password)

		if ('failed' in data):
			return False

		jsonData = json.loads(data)
		if ('error' in jsonData):
			return False
		else:
			self.UserDevKey = jsonData['key']
			return True

	def InsertDevice (self, device):
		data = self.GetRequest(self.ServerUri + "insert/device/" + self.UserDevKey + "/" + str(device.Type) + "/" + device.UUID + "/" + device.OSType + "/" + device.OSVersion + "/" + device.BrandName)

		if ('failed' in data):
			return "", False

		if ('info' in data):
			return data, True

		return False
	
	def RegisterDevice (self, device):
		jdata = json.dumps([{"key":"" + str(self.UserDevKey) + "", "payload":{"uuid":"" + str(device.UUID) + "","type":"" + str(device.Type) + "","ostype":"" + str(device.OSType) + "","osversion":"" + str(device.OSVersion) + "","brandname":"" + str(device.BrandName) + ""}}])
		data = self.PostRequset(self.ServerUri + "device/register/", jdata)

		if ('info' in data):
			return data, True
		
		return "", False

	def RegisterDeviceToPublisher (self, publisher, subscriber):
		jdata = json.dumps([{"key":"" + str(self.UserDevKey) + "", "payload":{"publisher_uuid":"" + str(publisher) + "","listener_uuid":"" + str(subscriber) + ""}}])
		data = self.PostRequset(self.ServerUri + "register/device/node/listener", jdata)

		if ('info' in data):
			return data, True
		
		return "", False

	def WSConnection_OnMessage_Handler (self, ws, message):
		data = json.loads(message)
		self.OnDataArrivedCallback(data)

	def WSConnection_OnError_Handler (self, ws, error):
	    self.OnErrorCallback()
	    print (error)

	def WSConnection_OnClose_Handler (self, ws):
		self.State = "DISCONN"
		self.OnConnectionClosedCallback()
		
	def WSConnection_OnOpen_Handler (self, ws):
		self.State = "CONN"
		self.OnConnectionCallback()

	def NodeWebfaceSocket_Thread (self):
		print("(MkSNetwork)# Connect Gateway ...")
		self.WSConnection.keep_running = True
		self.WSConnection.run_forever()
		print("(MkSNetwork)# Disconnect Gateway ...")

	def Disconnect(self):
		self.WSConnection.keep_running = False
		time.sleep(1)

	def AccessGateway (self, key, payload):
		# Set user key, commub=nication with applications will be based on key.
		# Key will be obtain by master on provisioning flow.
		self.UserDevKey 				= key
		self.BasicProtocol 				= MkSBasicNetworkProtocol.BasicNetworkProtocol(key)
		websocket.enableTrace(False)
		self.WSConnection 				= websocket.WebSocketApp(self.WSServerUri)
		self.WSConnection.on_message 	= self.WSConnection_OnMessage_Handler
		self.WSConnection.on_error 		= self.WSConnection_OnError_Handler
		self.WSConnection.on_close 		= self.WSConnection_OnClose_Handler
		self.WSConnection.on_open 		= self.WSConnection_OnOpen_Handler
		self.WSConnection.header		= 	{
											'uuid':self.DeviceUUID, 
											'node_type':str(self.Type), 
											'payload':str(payload), 
											'key':key
											}
		self.Disconnect()
		print("# TODO - This thread will be created each time whrn connection lost or on retry!!!")
		thread.start_new_thread(self.NodeWebfaceSocket_Thread, ())

		return True

	def SetDeviceUUID (self, uuid):
		self.DeviceUUID = uuid

	def SetDeviceType (self, type):
		self.Type = type
		
	def SetApiUrl (self, url):
		self.ServerUri = url
		
	def SetWsUrl (self, url):
		self.WSServerUri = url

	def SendWebSocket(self, packet):
		if packet is not "" and packet is not None:
			self.WSConnection.send(packet)
		else:
			print ("[Node]# Sending packet to Gateway FAILED")

	def SendKeepAlive(self):
		self.WSConnection.send("{\"packet_type\":\"keepalive\"}")
	
	def SendMessage(self, payload):
		try:
			self.SendWebSocket(payload)
		except:
			return False
		
		return True
