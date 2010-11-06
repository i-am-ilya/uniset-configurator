# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_editor
from global_conf import *

# 1. Name
# 2. Sensor name
# 3. Lamp
# 4. NoHorn
# 5. NoConfirm
# 6. Delay 
# 7. element type [Panel|Item] 
# 8. xmlnode | 9. sensor_xmlnode | 10. lamp_xmlnode

# field id
class fid():
   name = 0
   sensor = 1
   lamp = 2
   nohorn = 3
   noconfirm = 4
   tname = 5
   delay = 6
   etype = 7
   xmlnode = 8
   s_xmlnode = 9
   l_xmlnode = 10
   maxnum = 11

'''
Задачи: настройщик для АПС панелей
'''
class APSPanelEditor(base_editor.BaseEditor,gtk.TreeView):

    def __init__(self, conf):

        gtk.TreeView.__init__(self)
        base_editor.BaseEditor.__init__(self,conf)

        conf.glade.signal_autoconnect(self)
        self.model = None
        self.modelfilter = None
  
        self.model = gtk.TreeStore(gobject.TYPE_STRING,\
                                    gobject.TYPE_STRING, \
                                    gobject.TYPE_STRING, \
                                    gobject.TYPE_STRING, \
                                    gobject.TYPE_STRING, \
                                    gobject.TYPE_STRING, \
                                    gobject.TYPE_STRING, \
                                    gobject.TYPE_STRING, \
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
        column = gtk.TreeViewColumn(_("Панель"), renderer, text=fid.name)
        column.set_clickable(False)
        self.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Датчик"), renderer,text=fid.sensor)
        column.set_clickable(False)
        self.append_column(column)
        
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Лампочка"), renderer,text=fid.lamp)
        column.set_clickable(False)
        self.append_column(column)
        
        renderer = gtk.CellRendererText()
#        r1 = gtk.CellRendererToggle()
#        r1.set_property('activatable', True)
#        self.r1.connect( 'toggled', self.col1_toggled_cb, model )
#        column = gtk.TreeViewColumn(_("Horn"), r1,text=4)
        column = gtk.TreeViewColumn(_("Без\nзвука"), renderer,text=fid.nohorn)
        column.set_clickable(False)
        self.append_column(column)
        column = gtk.TreeViewColumn(_("Без\nквитирования"), renderer,text=fid.noconfirm)
        column.set_clickable(False)
        self.append_column(column)
        
        column = gtk.TreeViewColumn(_("Текстовое имя"), renderer,text=fid.tname)
        column.set_clickable(False)
        self.append_column(column)                

        self.aps_params=[ \
            ["dlg","apspanel_dlg",None,True], \
            ["panel_popup","apspanel_popup",None,True], \
            ["item_popup","apspanel_item_popup",None,True], \
            ["dlg_id","apspanel_dlg_name","name",False], \
            ["dlg_horn1","apspanel_dlg_horn1","horn1",False], \
            ["dlg_horn2","apspanel_dlg_horn2","horn2",False], \
            ["dlg_hornblink1","apspanel_dlg_hornblink1","hornblink1",False], \
            ["dlg_hornblink2","apspanel_dlg_hornblink2","hornblink1",False], \
            ["dlg_hornreset","apspanel_dlg_hornreset","hornreset",False], \
            ["dlg_hornreset2","apspanel_dlg_hornreset2","hornreset2",False], \
            ["dlg_flamp","apspanel_dlg_flamp","flamp",False], \
            ["dlg_confirm","apspanel_dlg_confirm","confirm",False], \
            ["dlg_remoteconfirm","apspanel_dlg_remoteconfirm","remoteconfirm",False], \
            ["dlg_remotelamp","apspanel_dlg_remotelamp","remote_bs",False], \
            ["dlg_confirmlamp","apspanel_dlg_confirmlamp","confirmlamp",False], \
            ["dlg_testlamp","apspanel_dlg_testlamp","testlamp",False], \
            ["dlg_oncontrol","apspanel_dlg_oncontrol","onControl",False] \
        ]

        self.init_glade_elements(self.aps_params) 
        
#        self.aps_rm_params=[\
#            ["dlg_rm","lcaps_dlg_remove",None,True], \
#            ["rm_id","lcaps_rm_id",None,True], \
#            ["rm_lamps","lcaps_rm_lamps",None,True], \
#            ["rm_helpers","lcaps_rm_helpsens",None,True], \
#            ["rm_title","lcaps_dlg_rm_title",None,True] \
#        ]                
#        self.init_glade_elements(self.lc_rm_params) 
               
        self.item_params=[ \
            ["dlg_item","apspanel_dlg_item",None,True], \
            ["dlg_item_title","apspanel_dlg_item_title",None,True], \
            ["item_sensor","apspanel_dlg_sensor","name",False], \
            ["item_lamp","apspanel_dlg_lamp","lamp",False], \
            ["item_noconfirm","apspanel_dlg_noconfirm","noconfirm",False], \
            ["item_blink","apspanel_dlg_blink","blink",False], \
            ["item_onhorn","apspanel_dlg_onhorn","onhorn",False], \
            ["item_onflash","apspanel_dlg_onflash","onflash",False], \
            ["item_nohorn","apspanel_dlg_nohorn","nohorn",False], \
            ["item_always_alarm","apspanel_dlg_always_alarm","alway_alarm",False], \
            ["item_delay","apspanel_dlg_delay","delay",False], \
            ["item_delay","apspanel_dlg_offtime","offtime",False], \
            ["item_block","apspanel_dlg_block","block",False], \
            ["item_remoteconfirm","apspanel_dlg_remoteconfirm","remote_reset",False], \
            ["item_comment","apspanel_dlg_comment","comment",False] \
        ]
        self.init_glade_elements(self.item_params)
        
        self.build_tree()
 
    def build_tree(self):
        self.settings_node = self.conf.xml.findNode(self.conf.xml.getDoc(),"settings")[0]
        if self.settings_node == None:
            print "(APSPanelEditor::load_list): <settings> not found?!..."
            return
        
        node = self.conf.xml.firstNode(self.settings_node.children)
        while node != None:
            if node.name.upper() == "APSPANEL":
               pname = get_str_val(node.prop("name"))
               if pname == "":
                  print '**** Unknown <APSPanel name="?"'
                  node = self.conf.xml.nextNode(node)
                  continue

               p=[]
               for i in range(0,fid.maxnum):
                   p.append(None)
               
               p[fid.name] = pname
               p[fid.etype] = "P"

               iter = self.model.append(None,p)
               self.build_items(iter,node)
            node = self.conf.xml.nextNode(node)
    
    def buld_items(self, iter, xmlnode):
        node = self.conf.xml.firstNode(xmlnode.children)
        if node == None:
           return
        
        while node != None:
            plist = self.read_item_param(node)
            it1 = self.model.append(iter,plist)
            node = self.conf.xml.nextNode(node)
   
    def read_item_param(self,xmlnode):
        p=[]
        for i in range(0,fid.maxnum):
            p.append(None)
        
        p[fid.name] = get_str_val(xmlnode.prop("name"))
        p[fid.lamp] = get_str_val(xmlnode.prop("lamp"))
        p[fid.nohorn] = get_int_val(xmlnode.prop("nohorn"))
        p[fid.noconfirm] = get_int_val(xmlnode.prop("noconfirm"))
        p[fid.delay] = get_int_val(xmlnode.prop("delay"))
        p[fid.etype] = "I"
        p[fid.xmlnode] = xmlnode
        p[fid.s_xmlnode] = self.conf.find_sensor(get_str_val(xmlnode.prop("name")))
        p[fid.l_xmlnode] = self.conf.find_sensor(get_str_val(xmlnode.prop("lamp")))
        
        if p[fid.s_xmlnode] != None:
           s_node = p[fid.s_xmlnode]
           p[fid.sensor] = str("(%6s)%s" % (s_node.prop("id"),s_node.prop("name")))
           p[fid.tname] = get_str_val(s_node.prop("textname"))
        else:
           p[fid.sensor] = get_str_val(xmlnode.prop("name"))
           p[fid.tname] = ""

        return p

    def name_if_exist(self,node):
        if node == None:
           return ""
        return node.prop("name")
    
    def on_button_press_event(self, object, event):
        (model, iter) = self.get_selection().get_selected()

        if event.button == 3:                                                                                                                                                       
            if not iter: 
               self.panel_popup.popup(None, None, None, event.button, event.time)
               return False
            
            t = model.get_value(iter,fid.etype)
            if t == "P":
                self.panel_popup.popup(None, None, None, event.button, event.time)
                return False                                                                                                                                                         
            if t == "I":
                self.item_popup.popup(None, None, None, event.button, event.time)
                return False
            
        
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            if not iter:                                                                                                                                                                
               return False
            t = model.get_value(iter,fid.etype)
            if t == "P": 
               self.panel_edit(iter)
            elif t == "I":
               self.item_edit(iter)               
        
        return False
    
    def on_apspanel_add(self,menuitem):
        print "on add panel.."
        self.panel_edit(None)
    
    def on_apspanel_edit(self,menuitem):
        print "on edit panel.."
        (model, iter) = self.get_selection().get_selected()
        if not iter:
           return	         
        self.panel_edit(iter)       
    
    def on_apspanel_remove(self,menuitem):
        print "on remove panel.."
        (model, iter) = self.get_selection().get_selected()
        if not iter:
           return	         
    
    def on_apspanel_item_add(self,menuitem):
        print "on add item.."
        self.item_edit(None)        
    
    def on_apspanel_item_edit(self,menuitem):
        print "on edit item.."
        (model, iter) = self.get_selection().get_selected()
        if not iter:
           return	         
        self.item_edit(iter)       
    
    def on_apspanel_item_remove(self,menuitem):
        print "on remove item.."
        (model, iter) = self.get_selection().get_selected()
        if not iter:
           return   

    def panel_edit(self,iter):
        print "edit panel.."
    
    def item_edit(self,iter):
        print "edit panel.."

    def on_apspanel_dlg_btn_id_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_id.set_text(s.prop("name"))
    
    def on_apspanel_dlg_btn_horn1_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_horn1.set_text(s.prop("name"))
    
    def on_apspanel_dlg_btn_horn2_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_horn2.set_text(s.prop("name"))
        
    def on_apspanel_dlg_btn_hornblink1_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_hornblink1.set_text(s.prop("name"))
        
    def on_apspanel_dlg_btn_hornblink2_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_hornblink2.set_text(s.prop("name"))
        
    def on_apspanel_dlg_btn_hornreset_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_hornreset.set_text(s.prop("name"))
        
    def on_apspanel_dlg_btn_hornreset2_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_hornreset2.set_text(s.prop("name"))
        
    def on_apspanel_dlg_btn_flamp_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_flamp.set_text(s.prop("name"))
        
    def on_apspanel_dlg_btn_confirm_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_confirm.set_text(s.prop("name"))
        
    def on_apspanel_dlg_btn_remoteconfirm_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_remoteconfirm.set_text(s.prop("name"))
        
    def on_apspanel_dlg_btn_remotelamp_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_remotelamp.set_text(s.prop("name"))
        
    def on_apspanel_dlg_btn_confirmlamp_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_confirmlamp.set_text(s.prop("name"))
        
    def on_apspanel_dlg_btn_testlamp_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_testlamp.set_text(s.prop("name"))
        
    def on_apspanel_dlg_btn_oncontrol_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_oncontrol.set_text(s.prop("name"))

    def on_apspanel_dlg_btn_sensor_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.item_sensor.set_text(s.prop("name"))

    
    def on_apspanel_dlg_btn_lamp_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.item_lamp.set_text(s.prop("name"))

    
    def on_apspanel_dlg_btn_block_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.item_block.set_text(s.prop("name"))

    def on_apspanel_dlg_noconfirm_toggled(self, cbtn):
        self.noconfirm_list.set_sensitive( cbtn.get_active() )

def create_module(conf):
    return APSPanelEditor(conf)

def module_name():
    return "APSPanel"
