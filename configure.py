#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, UniXML


class Conf:
    def __init__ (self, fname,gladexml):
    	self.xml = UniXML.UniXML(fname)
    	self.glade = gladexml
