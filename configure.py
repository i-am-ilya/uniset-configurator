#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, UniXML, dlg_slist

class Conf:
    def __init__ (self, fname,gladexml):
    	self.xml = UniXML.UniXML(fname)
    	self.glade = gladexml

        self.dlg_slist = dlg_slist.SListDialog(self.xml)
        self.changes = 0

    def mark_changes(self):
        self.changes = 1

    def unmark_changes(self):
        self.changes = 0

    def is_changed(self):
        return self.changes
    
    def reopen(self, fname):
        self.xml.reopen(fname)
        self.dlg_slist.reopen(self.xml)
        self.changes = 0
