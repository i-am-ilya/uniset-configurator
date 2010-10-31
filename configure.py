#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, UniXML, dlg_xlist
import gtk
from global_conf import *

class Conf:
    def __init__ (self, fname,gladexml, datdir):
        
        self.xml = UniXML.UniXML(fname)
        self.glade = gladexml

        self.dlg_xlist = dlg_xlist.XListDialog(self.xml,self.glade)
        self.dlg_cur = None

        self.changes = 0
        self.nodes_editor = None
        self.datdir = datdir

        self.s_node = self.find_s_node()
        self.o_node = self.find_o_node()
        
        self.id_list = self.load_id_list()
   
    def load_id_list(self):
        lst = self.build_id_list("nodes")
        lst = lst + self.build_id_list("sensors")
        lst = lst + self.build_id_list("objects")
        lst = lst + self.build_id_list("controllers")
        lst = lst + self.build_id_list("services")
        lst.sort()
        return lst
    
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
    
    def o_dlg(self):
        if self.dlg_cur != "o":
            self.dlg_xlist.build_tree("objects")
            self.dlg_cur = "o"
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
        self.s_node = self.find_s_node()
        self.o_node = self.find_o_node()
        self.id_list = self.load_id_list()
        
    def find_s_node(self):
        return self.find_section("sensors")
    
    def find_o_node(self):
        return self.find_section("objects")
    
    def find_section(self,secname):
        node = self.xml.findNode(self.xml.getDoc(),secname)[0]
        if node == None:
           print "(configure): not found %s section" % secname
           raise Exception()
        
        return node.children
    
    def build_id_list(self, secname):
        lst = []
        node = self.find_section(secname)
        while node != None:
           lst.append([get_int_val(node.prop("id")),node])
           node = self.xml.nextNode(node)
        
        return lst
    
    def find_first_unused_id(self):
        return self.find_first_unused_id_in_list(self.id_list)
    
    def find_first_unused_id_in_list(self,id_list):
        if len(id_list) <= 0:
           return 1

        prev = 1
        # т.к. список отсортирован по возрастанию
        # то можно сразу проверить первый элемент
        if id_list[0][0] > prev:
           return prev
        
        prev = id_list[0][0]
        for i in id_list:
            if i[0] - prev >1:
               break
            prev = i[0]
        
        return prev+1
    
    def create_new_sensor(self,sname):
        i = self.find_first_unused_id()
        s_node = self.find_s_node().parent
        n = s_node.newChild(None,"item",None)
        n.setProp("name",sname)
        n.setProp("id",str(i))
        self.id_list.append([i,n])
        self.id_list.sort()
        return n
    
    def create_new_object(self,oname):
        i = self.find_first_unused_id()
        o_node = self.find_o_node().parent
        n = o_node.newChild(None,"item",None)
        n.setProp("name",oname)
        n.setProp("id",str(i))
        self.id_list.append([i,n])
        self.id_list.sort()
        return n