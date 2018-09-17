#!/usr/bin/python
import os
import sys

class LocalNodeCommands:
	def __init__(self):
		pass

	def GetHeader(self):
		return "MKS: Data\n"

	def GetFooter(self):
		return "\n"

	def GetLocalNodes(self):
		packet = GetHeader()
		packet += "{\"command\":\"get_local_nodes\",\"direction\":\"request\"}"
		packet += GetFooter()

		return packet

	def GetPort(self, uuid, node_type):
		packet = GetHeader()
		packet += "{\"command\":\"get_port\",\"direction\":\"request\",\"uuid\":\"" + uuid + "\",\"type\":" + str(node_type) + "}"
		packet += GetFooter()

		return packet

	def GetMasterInfo(self, host_name, nodes):
		packet = GetHeader()
		packet += "{\"command\":\"get_master_info\",\"direction\":\"response\",\"info\":{\"hostname\":\"" + host_name + "\",\"nodes\":[" + nodes + "]}}"
		packet += GetFooter()

		return packet