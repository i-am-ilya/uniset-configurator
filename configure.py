#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, UniXML, dlg_slist, dlg_nodes
import gtk

class Conf:
    def __init__ (self, fname,gladexml):
    	self.xml = UniXML.UniXML(fname)
    	self.glade = gladexml

        self.dlg_slist = dlg_slist.SListDialog(self.xml)
        self.dlg_nodes = dlg_nodes.NodesDialog(self.xml)
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
    
    def get_cb_param(self, checkbutton):
        if checkbutton.get_active():
            return "1"
        return ""
    
    def set_combobox_element(self,cbox,val):
        model = cbox.get_model()
        it = model.get_iter_first()
        while it is not None:                     
            if val.upper() == str(model.get_value(it,0)).upper():
                 cbox.set_active_iter(it)
                 return
            it = model.iter_next(it)     