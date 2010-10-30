# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_editor
from global_conf import *

'''
Задачи: настройщик для алгоритма управления свето-звуковой сигнализацией на колонках
'''
class LCAPSEditor(base_editor.BaseEditor,gtk.TreeView):

    def __init__(self, conf):

        gtk.TreeView.__init__(self)
        base_editor.BaseEditor.__init__(self,conf)

        conf.glade.signal_autoconnect(self)
        self.model = None
        self.modelfilter = None
        #  Name | Sensor name | Lamp name | FlashLamp name | Horn yes/no | element type [Lcaps|Item] | xmlnode | sensor_xmlnode | lamp_xmlnode | horn_xmlnode 
        self.model = gtk.TreeStore(gobject.TYPE_STRING,\
                                    gobject.TYPE_STRING, \
                                    gobject.TYPE_STRING, \
                                    gobject.TYPE_STRING, \
                                    gobject.TYPE_STRING, \
                                    gobject.TYPE_STRING, \
                                    object,\
                                    object,\
                                    object,\
                                    object)
        
        self.modelfilter = self.model.filter_new()

#       self.modelfilter.set_visible_column(1)

        # create treeview
        self.set_model(self.model)
        self.set_rules_hint(True)
        self.connect("button-press-event", self.on_button_press_event)
        
        
        
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Lighting column"), renderer, text=0)
        column.set_clickable(False)
        self.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Lamp"), renderer,text=1)
        column.set_clickable(False)
        self.append_column(column)
        
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Sensor"), renderer,text=2)
        column.set_clickable(False)
        self.append_column(column)
        
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Light"), renderer,text=3)
        column.set_clickable(False)
        self.append_column(column)
        
        renderer = gtk.CellRendererText()
#        r1 = gtk.CellRendererToggle()
#        r1.set_property('activatable', True)
#        self.r1.connect( 'toggled', self.col1_toggled_cb, model )
#        column = gtk.TreeViewColumn(_("Horn"), r1,text=4)
        column = gtk.TreeViewColumn(_("Horn"), renderer,text=4)        
        column.set_clickable(False)
        self.append_column(column)
                
        self.lcnew_params=[ \
            ["dlg_lcnew","lcaps_dlg_lcnew",None,True], \
            ["lcaps_popup","lcaps_popup",None,True], \
            ["item_popup","lcaps_item_popup",None,True] \
        ]
        self.init_glade_elements(self.lcnew_params)        
        self.item_params=[ \
            ["dlg_lcaps","lcaps_dlg",None,True], \
            ["dlg_lcaps_title","lcaps_dlg_title",None,True], \
            ["item_sensor","lcaps_dlg_sensor","name",False], \
            ["item_lamp","lcaps_dlg_lamp","lamp",False], \
            ["item_horn","lcaps_dlg_horn","horn",False], \
            ["item_noconfirm","lcaps_dlg_noconfirm","noconfirm",False], \
            ["item_delay","lcaps_dlg_delay","delay",False], \
            ["item_comment","lcaps_dlg_comment","comment",False] \
        ]
        self.init_glade_elements(self.item_params)

        self.s_node = self.conf.xml.findNode(self.conf.xml.getDoc(),"sensors")[0]
        if self.s_node == None:
           print "(LCAPSEditor): not found <sensors> section"
           raise Exception()
        self.s_node = self.s_node.children

        self.build_lcaps_list()
        self.show_all()
    
    def build_lcaps_list(self):
        setnode = self.conf.xml.findNode(self.conf.xml.getDoc(),"settings")[0]
        if setnode == None:
            print "(LCAPSEditor::build_lcaps_list): <settings> not found?!..."
            return
        
        node = self.conf.xml.firstNode(setnode.children)
        while node != None:
            if node.name.upper() == "LCAPS":
               lname = get_str_val(node.prop("name"))
               print "find LCAPS: " + lname
#  Name | Lamp name | Sensor | FlashLamp name | Horn yes/no | element type [Lcaps|Item] | xmlnode | sensor_xmlnode | lamp_xmlnode | horn_xmlnode 
               horn_name = get_str_val(node.prop("horn"))
               horn_node = None
               if horn_name != "":
                  horn_node = self.find_sensor(horn_name)

               iter1 = self.model.append(None,[lname,"","","","","L",node,None,None,horn_node])
               self.build_orange_list(iter1,node)
               self.build_red_list(iter1,node)
               self.build_green_list(iter1,node)
               
            node = self.conf.xml.nextNode(node)    
    
    def build_orange_list(self, lc_iter, xmlnode):
        o_node = self.conf.xml.findNode(xmlnode,"orange")[0]
        if o_node == None:
           return
        node = self.conf.xml.firstNode(o_node.children)
        while node != None:
            plist = self.read_item_param(lc_iter,node,o_node)
            it = self.model.append(lc_iter,plist)
            node = self.conf.xml.nextNode(node)
    
    def build_green_list(self, lc_iter, xmlnode):
        pass
    
    def build_red_list(self, lc_iter, xmlnode):
        pass
    
    def read_item_param(self, i_iter, xmlnode,parent_xmlnode):
        nohorn = 0
        if get_int_val(xmlnode.prop("nohorn")) > 0:
           nohorn = 1
        
        return [ "", \
              get_str_val(xmlnode.prop("lamp")), \
              get_str_val(xmlnode.prop("name")), \
              get_str_val(parent_xmlnode.prop("name")), \
              nohorn, \
              "I", \
              xmlnode, \
              self.find_sensor(get_str_val(xmlnode.prop("name"))), \
              self.find_sensor(get_str_val(xmlnode.prop("lamp"))), \
              None \
        ]
    
    def find_sensor(self, name):
        node = self.s_node
        while node != None:
            if get_str_val(node.prop("name")) == name:
               return node
            node = self.conf.xml.nextNode(node)           
        return None
    
    def find_sensor_by_id(self, sid):
        node = self.s_node
        while node != None:
            if get_int_val(node.prop("id")) == sid:
               return node
            node = self.conf.xml.nextNode(node)
        return None
    
    def on_button_press_event(self, object, event):
        (model, iter) = self.get_selection().get_selected()

        if event.button == 3:                                                                                                                                                       
            if not iter: return False
            t = model.get_value(iter,5)
            if t == "L":
                self.lcaps_popup.popup(None, None, None, event.button, event.time)                                                                                                       
                return False                                                                                                                                                         
            if t == "I":
                self.item_popup.popup(None, None, None, event.button, event.time)                                                                                                       
                return False

        
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            if not iter:                                                                                                                                                                
               return False
            t = model.get_value(iter,5)
            if t == "L": 
               self.on_edit_lcaps(iter)
            elif t == "I":
               self.on_edit_item(iter)               
        
        return False
    
    def on_lcaps_item_add(self,menuitem):
        self.on_edit_item(None)
    
    def on_lcaps_item_edit(self,menuitem):
        (model, iter) = self.get_selection().get_selected()
        self.on_edit_item(iter)
    
    def on_lcaps_item_remove(self,menuitem):
        print "***** item remove***"
    
    def on_lcaps_add(self,menuitem):
        self.on_edit_lcaps(None)
    
    def on_lcaps_edit(self,menuitem):
        (model, iter) = self.get_selection().get_selected()
        self.on_edit_lcaps(iter)
    
    def on_lcaps_remove(self,menuitem):
       (model, iter) = self.get_selection().get_selected()
       if not iter:
          return
    
    def on_edit_lcaps(self,lc_iter):
        print "***** edit lcaps: iter" + str(lc_iter)

    def on_edit_item(self,i_iter):
        print "***** edit item: iter" + str(i_iter)
    
    def on_lcpas_dlg_btn_lamp_clicked(self, button):
        print "***** btn_lamp_clicked***"
    
    def on_lcpas_dlg_btn_sensor_clicked(self, button):
        print "***** btn_sensor_clicked***"
    
    def on_lcaps_dlg_id_create_clicked(self, button):
        print "***** id create_clicked***"
    
    def on_lcaps_dlg_id_sel_clicked(self, button):
        print "***** id select clicked***"
    
    def on_lcaps_dlg_btn_heartbeat_clicked(self, button):
        print "***** heartbeat clicked**"
        