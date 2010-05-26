#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, UniXML, dlg_slist

class Conf:
    def __init__ (self, fname,gladexml):
    	self.xml = UniXML.UniXML(fname)
    	self.glade = gladexml

        self.dlg_slist = dlg_slist.SListDialog(self.xml)
#        self.dlg_slist = gladexml.get_widget("dlg_slist")                                                                                                                                           
#        scwin_list = gladexml.get_widget("scwin_slist")                                                                                                                                         
#        self.slist = slist.SList(self.xml,self.dlg_slist)                                                                                                                                                           
#        scwin_list.add(self.slist)
        