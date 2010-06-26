#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, UniXML, dlg_xlist
import gtk

class Conf:
    def __init__ (self, fname,gladexml):
        
        self.xml = UniXML.UniXML(fname)
        self.glade = gladexml

        self.dlg_xlist = dlg_xlist.XListDialog(self.xml,self.glade)
        self.dlg_cur = None

        self.changes = 0
   
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

    def mark_changes(self):
        self.changes = 1

    def unmark_changes(self):
        self.changes = 0

    def is_changed(self):
        return self.changes
    
    def reopen(self, fname):
        self.xml.reopen(fname)
        self.dlg_cur = None
        self.changes = 0
    
    def check_value_int(self, val):                                         
        try:
            x = int(val)
            return True
        except ValueError, NameError:
             return False
    
    def get_int_val(self,str_val):
        if str_val == "" or str_val == None: 
            return 0
        return int(str_val)

    def get_str_val(self,str_val):
        if str_val == None: 
            return ""
        return str_val
