# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import re
import datetime
import UniXML
import configure
import base_editor
from global_conf import *

class fid():
  name = 0
  textname = 1
  rawxml = 2
  xmlnode = 3

'''
Задачи:
1. Добавление, удаление карт ввода/вывода на узлах
2. Редактирование параметров каждого канала
'''
class Viewer(base_editor.BaseEditor,gtk.Viewport):

    def __init__(self, conf):

        base_editor.BaseEditor.__init__(self,conf)
        gtk.Viewport.__init__(self)
        #gtk.VBox.__init__(self)

        self.glade = gtk.glade.XML(conf.datdir+"viewer.glade")
        self.glade.signal_autoconnect(self)

        self.elements = [ \
             ["cbID","cbID"], \
             ["cbName", "cbName"], \
             ["cbTextName","cbTextName"], \
             ["cbFilter", "cbFilter"], \
             ["entField", "ent_field"], \
             ["entValue", "ent_value"], \
             ["lblCount", "lblCount"], \
             ["fentry", "filter_entry"], \
             ["filter_cb_case", "filter_cb_case"] \
        ]
        self.init_glade_elements(self.elements,self.glade)

        vbox = self.glade.get_widget("mainbox")
        vbox.reparent(self)

        box = self.glade.get_widget("tree_win")
        self.tv = gtk.TreeView()
        self.tv.show_all()
        box.add(self.tv)

        # подключение к редактору узлов (для отслеживания изменений в списке узлов)
#        n_editor = conf.n_editor()
#       if n_editor != None:
#            n_editor.connect("change-node",self.nodeslist_change)
#            n_editor.connect("add-new-node",self.nodeslist_add)
#            n_editor.connect("remove-node",self.nodeslist_remove)

        self.model = None
        self.modelfilter = None
        self.model = gtk.TreeStore(gobject.TYPE_STRING, # name
                                   gobject.TYPE_STRING, # textname
                                   gobject.TYPE_STRING, # raw xml text
                                   object)              # xmlnode
        
        self.fmodel = self.model.filter_new()
        self.fmodel.set_visible_func(self.view_filter_func)
        self.tv.set_model(self.fmodel)
        self.tv.set_rules_hint(True)
        self.tv.set_enable_tree_lines(True)
        self.tv.set_grid_lines(True)
#        self.tv.connect("button-press-event", self.on_button_press_event)
        
        column = gtk.TreeViewColumn(_("Name"))
        nmcell = gtk.CellRendererText()
        pbcell = gtk.CellRendererPixbuf()
        column.pack_start(pbcell, False)
        column.pack_start(nmcell, False)
        column.set_attributes(nmcell,text=fid.name)
        column.set_clickable(False)
        self.tv.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Text name"), renderer, text=fid.textname)
        column.set_clickable(False)
        self.tv.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("XML"), renderer, text=fid.rawxml)
        column.set_clickable(False)
        self.tv.append_column(column)

        self.reopen()
        self.show_all()
    
    def reopen(self):
        self.model.clear()
        self.build_tree()

    def build_tree(self):
        node = self.conf.xml.findNode(self.conf.xml.getDoc(),"sensors")[0].children.next
        while node != None:
            info = self.get_rawxml_text(node)
            self.model.append(None,[node.prop("name"),node.prop("textname"),info,node])
            node = self.conf.xml.nextNode(node)

    def get_rawxml_text(self,xmlnode):
        return str(xmlnode)

    def find_str(self, s1, s2, case):

        if s1 == None or s2 == None:
           return False

        if case == False:
           if s1.upper().find(s2.upper()) != -1:
                return True
           return False

        if s1.find(s2) != -1:
             return True

        return False

    def filter_entry_changed(self,entry):
        self.fmodel.refilter()

    def filter_cb_toggled(self,checkbtn):
        self.fmodel.refilter()
             
    def view_filter_func(self, model, it):
        res = self.check_filters(model, it)
        self.lblCount.set_text( str(len(self.fmodel)) )
        #print "Count: %d" % len(self.fmodel)
        return res
           

    def check_filters(self, model, it):

        if it == None:
           return True

        if self.entField.get_text() != "":
           xmlnode = model.get_value(it,fid.xmlnode)
           if self.entValue.get_text() != "":
              if xmlnode.prop(self.entField.get_text()) !=  self.entValue.get_text():
                 return False
           elif to_str(xmlnode.prop(self.entField.get_text())) == "":
              return False
           
        t = self.fentry.get_text()
        if t == "":
             return True

        xmlnode = model.get_value(it,fid.xmlnode)

        # если привязки ещё нет, то не отображаем
        if xmlnode == None:
           return False

        if self.cbID.get_active() and self.find_str( xmlnode.prop("id"), t, self.filter_cb_case.get_active() ):
           return True

        if self.cbName.get_active() and self.find_str( xmlnode.prop("name"), t, self.filter_cb_case.get_active() ):
           return True

        if self.cbTextName.get_active() and self.find_str( xmlnode.prop("textname"), t, self.filter_cb_case.get_active() ):
           return True


        return False

    def cb_toggled(self,btn):
        self.fmodel.refilter()

    def entry_changed(self,entry):
        self.fmodel.refilter()


def create_module(conf):
    return Viewer(conf)

def module_name():
    return "Список датчиков"
