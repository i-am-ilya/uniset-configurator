#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: UniXML.py,v 1.3 2006/09/12 16:57:28 lav Exp $

import sys
import libxml2

class UniXML(str):
	def __init__(self, str):
		try:
			self.doc = None
			self.doc = libxml2.parseFile(str)
		except libxml2.parserError:
#			print "parsing error, maybe file not found?"
			sys.exit(-1)
		print "parsing " + self.doc.name
		libxml2.registerErrorHandler(self.callback, "-->")

	def __del__(self):
		if self.doc != None:
			self.doc.freeDoc()
		libxml2.cleanupParser()
		if libxml2.debugMemory(1) != 0:
			print "Memory leak %d bytes" % (libxml2.debugMemory(1))
			libxml2.dumpMemory()
		
	def callback(ctx, str):
		print "%s %s" % (ctx, str)

	def getDoc(self):
		return self.doc

	def findNode(self, node, nodestr="", propstr=""):
		while node != None:
			if node.name == nodestr:
				return [node, node.name, node.prop(propstr)]
			ret = self.findNode(node.children, nodestr, propstr)
			if ret[0] != None:
				return ret
			node = node.next
		return [None, None, None]

	def findNode_byProp(self, node, propstr, valuestr):
#		print node 
#		print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
		while node != None:
			if node.prop(propstr) == valuestr:
				return [node, node.name, node.prop(propstr)]
			ret = self.findNode_byProp (node.children, propstr, valuestr)
			if ret[0] != None:
				return ret
			node = node.next
		return [None, None, None]

#		res_list = []
#		node_current = node.children
#		while node_current != None:
#		    print "children " + str(node_current)
#		    if node_current.prop(propstr) == valuestr:
#			res_list.append (node_current)
#		    node_current.next()     
#		return res_list



	def nextNode(self, node):
		while node != None:
			node = node.next
			if node == None:
				return node
			if node.name != "text" and node.name != "comment":
				return node

	def getProp(self, node, str):
		prop = node.prop(str)
		if prop != None:
			return prop
		else:
			return ""
