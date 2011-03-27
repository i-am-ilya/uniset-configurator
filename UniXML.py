#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import libxml2
import xml.dom.minidom as md
import re
# ----------------------------- 
class EmptyNode():
    
    def __init__(self):
        self.props = dict()
     
    def prop(self,name):
        try:
            return self.props[name]
        except KeyError,ValueError:
            pass
        
        return ""
     
    def setProp(self,name,val):
        self.props[name] = val
# -----------------------------  
class UniXML(str):
    def __init__(self, str):
        try:
            self.doc = None
            self.fname = str
            self.doc = libxml2.parseFile(str)
        except libxml2.parserError:
            sys.exit(-1)
#        print "parsing " + self.doc.name
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

    def getFileName(self):
        return self.fname

    def findNode(self, node, nodestr="", propstr="", recur=True):
        while node != None:
            if node.name == nodestr:
                return [node, node.name, node.prop(propstr)]
            if recur == True:
               ret = self.findNode(node.children, nodestr, propstr)
               if ret[0] != None:
                  return ret
            node = node.next
        return [None, None, None]

    def findMyLevel(self, node, nodestr="", propstr=""):
        while node != None:
            if node.name == nodestr:
                return [node, node.name, node.prop(propstr)]
            node = node.next
        return [None, None, None]
    
    def findNode_byProp(self, node, propstr, valuestr, recur=True):
        while node != None:
            if node.prop(propstr) == valuestr:
                return [node, node.name, node.prop(propstr)]
            if recur == True:
               ret = self.findNode_byProp (node.children, propstr, valuestr)
               if ret[0] != None:
                  return ret
            node = node.next
        return [None, None, None]
    
    def nextNode(self, node):
        while node != None:
            node = node.next
            if node == None:
                return node
            if node.name != "text" and node.name != "comment":
                  return node
        return None

    def getNode(self, node):
        if node == None:
           return None
        if node.name != "text" and node.name != "comment":
           return node
        return self.nextNode(node)

    def firstNode(self, node):
        while node != None:
            prev = node
            node = node.prev
            if node == None:
                node = prev
                break
        return self.getNode(node)
        
    def getProp(self, node, str):
        prop = node.prop(str)
        if prop != None:
            return prop
        else:
            return ""
    
    def unlink(self,node):
        if node != None:
           node.unlinkNode()

    def save(self, filename=None, pretty_format=True):
        if filename == None:
           filename = self.fname
        
        if pretty_format == True:
		   return self.pretty_save(filename)

        return self.doc.saveFile(filename)

    def reopen(self, filename):
        try:
            self.doc.freeDoc()
            self.fname = filename
            self.doc = libxml2.parseFile(filename)
        except libxml2.parserError:
            sys.exit(-1)

    def pretty_save(self, filename):
        context = self.doc.serialize(encoding="utf-8")
        mdoc = md.parseString(context) 
        s = mdoc.toprettyxml(encoding="utf-8").split("\n")
        out = open(filename,"w")
        p = re.compile(r'\ [^\s]{1,}=""')
        for l in s:
            if l.strip():
               # удаяем пустые свойства prop=""
               l = p.sub('', l)
               out.write(l+"\n")
        out.close()
