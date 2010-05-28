#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: UniXML.py,v 1.3 2006/09/12 16:57:28 lav Exp $

import sys
import libxml2

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
        while node != None:
            if node.prop(propstr) == valuestr:
                return [node, node.name, node.prop(propstr)]
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

    def getProp(self, node, str):
        prop = node.prop(str)
        if prop != None:
            return prop
        else:
            return ""

    def save(self, filename=None):
        if filename == None:
           filename = self.fname
        return self.doc.saveFile(filename)

    def reopen(self, filename):
        try:
            self.doc.freeDoc()
            self.fname = filename
            self.doc = libxml2.parseFile(filename)
        except libxml2.parserError:
            sys.exit(-1)
