#!/usr/bin/python
import os
import time
import json

class BasicNetworkProtocol():
	def __init__(self, key):
		self.Name 	= "Message Protocol Between Nodes and Applications"
		self.Key    = key

	def GetUUIDFromJson(self, json):
		return json['uuid']

	def GetValueFromJson(self, json):
		return json['value']
	
	def GetMessageTypeFromJson(self, json):
		return json['header']['message_type']

	def GetSourceFromJson(self, json):
		return json['header']['source']

	def GetDestinationFromJson(self, json):
		return json['header']['destination']

	def GetDataFromJson(self, json):
		return json['data']

	def GetCommandFromJson(self, json):
		return json['data']['header']['command']

	def GetPayloadFromJson(self, json):
		return json['data']['payload']
    
	def BuildMessage(self, direction, messageType, destination, source, command, payload, piggy):
		message = {
			'header': {
				'message_type': str(messageType),
				'destination': str(destination),
				'source': str(source),
				'direction': str(direction)
			},
			'data': {
				'header': { 
					'command': str(command), 
					'timestamp': str(int(time.time())) 
				},
				'payload': payload
			},
			'user': {
				'key': str(self.Key)
			},
			'additional': {

			},
			'piggybag': piggy
		}

		return json.dumps(message)
    
	def BuildRequest(self, messageType, destination, source, command, payload, piggy):
		return self.BuildMessage("request", messageType, destination, source, command, payload, piggy)
    
	def BuildResponse(self, packet, payload):
		dest 	= packet['header']['destination']
		src 	= packet['header']['source']

		packet['header']['destination']	= src
		packet['header']['source']		= dest
		packet['header']['direction']	= "response"
		packet['data']['payload']		= payload

		return json.dumps(packet)