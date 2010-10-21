#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, UniXML, dlg_xlist
import gtk

class Conf:
    def __init__ (self, fname,gladexml, datdir):
        
        self.xml = UniXML.UniXML(fname)
        self.glade = gladexml

        self.dlg_xlist = dlg_xlist.XListDialog(self.xml,self.glade)
        self.dlg_cur = None

        self.changes = 0
        self.nodes_editor = None
        self.datdir = datdir
   
    def s_dlg(self):
        if self.dlg_cur != "s":
            self.dlg_xlist.build_tree("sensors")
            self.dlg_cur = "s"
        return self.dlg_xlist
    
    def n_dlg(self):
        if self.dlg_cur != "n":
            self.dlg_xlist.build_tree("nodes")
            self.dlg_cur = "n"
        
        return self.dlg_xlist
    
    def n_editor(self):
        return self.nodes_editor
    
    def set_nodes_editor(self, editor):
        self.nodes_editor = editor

    def mark_changes(self):
        self.changes = 1

    def unmark_changes(self):
        self.changes = 0

    def is_changed(self):
        return self.changes
    
    def n_reopen(self):
        if self.dlg_cur == "n":
            self.dlg_xlist.build_tree("nodes")
    
    def s_reopen(self):
        if self.dlg_cur == "s":
            self.dlg_xlist.build_tree("sensors")

    def reopen(self, fname):
        self.xml.reopen(fname)
        self.dlg_cur = None
        self.changes = 0
  
 