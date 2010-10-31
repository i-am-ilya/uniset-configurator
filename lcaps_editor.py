# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_editor
from global_conf import *

# 1. Name/Lamp Num 
# 2. Sensor name
# 3. FlashLamp type 
# 4. NoHorn
# 5. NoConfirm
# 6. Delay 
# 7. element type [Lcaps|Item] 
# 8. xmlnode | 9. sensor_xmlnode | 10. lamp_xmlnode
# field id
class fid():
   name = 0
   sensor = 1
   flamp = 2
   nohorn = 3
   noconfirm = 4
   delay = 5
   etype = 6
   xmlnode = 7
   s_xmlnode = 8
   l_xmlnode = 9
   maxnum = 10

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
  
        self.model = gtk.TreeStore(gobject.TYPE_STRING,\
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
        column = gtk.TreeViewColumn(_("Колонка"), renderer, text=fid.name)
        column.set_clickable(False)
        self.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Датчик"), renderer,text=fid.sensor)
        column.set_clickable(False)
        self.append_column(column)
        
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Маячок"), renderer,text=fid.flamp)
        column.set_clickable(False)
        self.append_column(column)
        
        renderer = gtk.CellRendererText()
#        r1 = gtk.CellRendererToggle()
#        r1.set_property('activatable', True)
#        self.r1.connect( 'toggled', self.col1_toggled_cb, model )
#        column = gtk.TreeViewColumn(_("Horn"), r1,text=4)
        column = gtk.TreeViewColumn(_("Без звука"), renderer,text=fid.nohorn)
        column.set_clickable(False)
        self.append_column(column)
        column = gtk.TreeViewColumn(_("Без квитирования"), renderer,text=fid.noconfirm)
        column.set_clickable(False)
        self.append_column(column)
                
        self.lcnew_params=[ \
            ["dlg_lcnew","lcaps_dlg_lcnew",None,True], \
            ["lcaps_popup","lcaps_popup",None,True], \
            ["item_popup","lcaps_item_popup",None,True], \
            ["dlg_lc_name","lcaps_dlg_name",None,True], \
            ["dlg_horn","lcaps_dlg_horn",None,True], \
            ["dlg_hornreset","lcaps_dlg_hornreset",None,True], \
            ["dlg_confirm","lcaps_dlg_confirm",None,True], \
            ["dlg_lc_count","lcaps_dlg_lc_count",None,True], \
            ["dlg_heartbeat","lcaps_dlg_heartbeat",None,True] \
        ]
                
        self.init_glade_elements(self.lcnew_params)        
        self.item_params=[ \
            ["dlg_lcaps","lcaps_dlg",None,True], \
            ["dlg_lcaps_title","lcaps_dlg_title",None,True], \
            ["item_sensor","lcaps_dlg_sensor","name",False], \
            ["item_lamp","lcaps_dlg_lamp","lamp",False], \
            ["item_horn","lcaps_dlg_cb_horn","horn",False], \
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
        
        self.lc_list = dict()
        self.load_lcaps_list()
        self.build_lcaps_tree()
        self.show_all()
    
    def load_lcaps_list(self):
        self.setnode = self.conf.xml.findNode(self.conf.xml.getDoc(),"settings")[0]
        if self.setnode == None:
            print "(LCAPSEditor::build_lcaps_list): <settings> not found?!..."
            return
        
        node = self.conf.xml.firstNode(self.setnode.children)
        while node != None:
            if node.name.upper() == "LCAPS":
               lname = get_str_val(node.prop("name"))
               print "find LCAPS: " + lname

               item_list = self.load_item_list(node,"orange") + \
                                self.load_item_list(node,"red") + \
                                self.load_item_list(node,"green")
               
               item_list.sort()
               
               lc_params = dict()
               lc_params['name'] = lname
               lc_params['xmlnode'] = node
               lc_params['list'] = item_list
               lc_params['horn'] = self.init_sensor(node,"horn")
               lc_params['hornreset'] = self.init_sensor(node,"hornreset")
               lc_params['confirm'] = self.init_sensor(node,"confirm")
               lc_params['heartbeat_id'] = self.init_sensor(node,"heartbeat_id")
               lc_params['heartbeat_max'] = self.init_sensor(node,"heartbeat_max")
               lc_params['orange'] = self.conf.xml.findNode(node,"orange")[0]
               lc_params['green'] = self.conf.xml.findNode(node,"green")[0]
               lc_params['red'] = self.conf.xml.findNode(node,"red")[0]
               
               self.lc_list[lname] = lc_params
            
            node = self.conf.xml.nextNode(node)
    
    def save_lclist_2xml(self):
        
        for key, lc in self.lc_list.items():
            lc_node = lc['xmlnode']
            
            lc_node.setProp("confirm",self.name_if_exist(lc['confirm']))
            lc_node.setProp("horn",self.name_if_exist(lc['horn']))
            lc_node.setProp("hornreset",self.name_if_exist(lc['hornreset']))
            lc_node.setProp("heartbeat_id",self.name_if_exist(lc['heartbeat_id']))
            lc_node.setProp("heartbeat_max",lc['heartbeat_max'])
            for i in lc['list']:
                i_node = i[fid.xmlnode]
                i_node.setProp("num",i[fid.name])
                i_node.setProp("name",i[fid.sensor])
                i_node.setProp("lamp",self.get_lamp_name(key,i[fid.name]))
                i_node.setProp("nohorn",str(i[fid.nohorn]))
                i_node.setProp("noconfirm",str(i[fid.noconfirm]))
                i_node.setProp("delay",str(i[fid.delay]))
    
    def name_if_exist(self,node):
        if node == None:
           return ""
        return node.prop("name")
    
    def init_sensor(self,xmlnode,prop):
        name = get_str_val(xmlnode.prop(prop))
        node = None
        if name != "":
           return self.find_sensor(name)
        
    def load_item_list(self, xmlnode,l_name):
        o_node = self.conf.xml.findNode(xmlnode,l_name)[0]
        if o_node == None:
           return []
        ret = []
        node = self.conf.xml.firstNode(o_node.children)
        while node != None:
            plist = self.read_item_param(node,l_name)
            ret.append(plist)
            node = self.conf.xml.nextNode(node)
        
        return ret
    
    def read_item_param(self,xmlnode,l_name):
        p=[]
        for i in range(0,fid.maxnum):
            p.append(None)
        
        p[fid.name] = get_str_val(xmlnode.prop("num"))
        p[fid.flamp] = self.get_light_name(l_name)
        p[fid.nohorn] = get_int_val(xmlnode.prop("nohorn"))
        p[fid.noconfirm] = get_int_val(xmlnode.prop("noconfirm"))
        p[fid.delay] = get_int_val(xmlnode.prop("delay"))
        p[fid.etype] = "I"
        p[fid.xmlnode] = xmlnode
        p[fid.s_xmlnode] = self.find_sensor(get_str_val(xmlnode.prop("name")))
        p[fid.l_xmlnode] = self.find_sensor(get_str_val(xmlnode.prop("lamp")))
        
        if p[fid.s_xmlnode] != None:
           s_node = p[fid.s_xmlnode]
           p[fid.sensor] = str("(%s)%s" % (s_node.prop("id"),s_node.prop("textname")))
        else:
           p[fid.sensor] = get_str_val(xmlnode.prop("name"))

        return p
     
    def get_light_name(self, name):
        if name.lower()=="orange":
           return "Оранжевый"
        if name.lower()=="red":
           return "Красный"
        if name.lower()=="green":
           return "Зелёный"
        return ""
    
    def get_lamp_name(self,lc_name,num):
        return "%s_Lamp%d_C"%(lc_name,int(num))
    
    def get_horn_name(self,lc_name,num):
        return "%s_Horn%d_C"%(lc_name,int(num))
    
    def find_sensor(self, name):
        node = self.s_node
        while node != None:
            if get_str_val(node.prop("name")) == name:
               return node
            node = self.conf.xml.nextNode(node)           
        return None
    
    def find_object(self, name):
        node = self.conf.find_o_node()
        while node != None:
            if get_str_val(node.prop("name")) == name:
               return node
            node = self.conf.xml.nextNode(node)    
        return None    
    
    def build_lcaps_tree(self):
        #self.lc_list.sort()
        for key, lc in self.lc_list.items():
            it1 = self.model.append(None,self.build_lc_param(lc))
            for i in lc['list']:
                it2 = self.model.append(it1,i)
    
    def build_lc_param(self,lc):
        p=[]
        for i in range(0,fid.maxnum):
            p.append(None)
        
        p[fid.name] = lc['name']
        p[fid.sensor] = ""
        p[fid.flamp] = ""
        p[fid.nohorn] = ""
        p[fid.noconfirm] = ""
        p[fid.delay] = ""
        p[fid.etype] = "L"
        p[fid.xmlnode] = lc['xmlnode']
        p[fid.s_xmlnode] = None
        p[fid.l_xmlnode] = None
        return p
    
    def on_button_press_event(self, object, event):
        (model, iter) = self.get_selection().get_selected()

        if event.button == 3:                                                                                                                                                       
            if not iter: return False
            t = model.get_value(iter,fid.etype)
            if t == "L":
                self.lcaps_popup.popup(None, None, None, event.button, event.time)                                                                                                       
                return False                                                                                                                                                         
            if t == "I":
                self.item_popup.popup(None, None, None, event.button, event.time)                                                                                                       
                return False

        
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            if not iter:                                                                                                                                                                
               return False
            t = model.get_value(iter,fid.etype)
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
        while True:
           res = self.dlg_lcnew.run()
           self.dlg_lcnew.hide()
           if res != dlg_RESPONSE_OK:
               return
           
           if self.dlg_lc_name.get_text() == "":
              dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,"Не задано имя")
              res = dlg.run()
              dlg.hide()
              continue
           
           if self.dlg_horn.get_text() == "":
              dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,"Не задано имя датчика 'horn'")
              res = dlg.run()
              dlg.hide()
              continue
           
           if self.dlg_hornreset.get_text() == "":
              dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,"Не задано имя датчика 'hornreset'")
              res = dlg.run()
              dlg.hide()
              continue
           
           if self.dlg_confirm.get_text() == "":
              dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,"Не задано имя датчика 'confirm'")
              res = dlg.run()
              dlg.hide()
              continue           

#           if self.dlg_heartbeat_name.get_text() == "":
#              dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,"Не задано имя датчика 'heartbeat'")
#              res = dlg.run()
#              dlg.hide()
#              continue
           if self.dlg_lc_count.get_value_as_int() <=1:
              msg = _("Одна лампочка ?! Уверены")
              dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,msg)
              res = dlg.run()
              dlg.hide()
              if res != gtk.RESPONSE_YES:
                 continue

           break

        lc_name = self.dlg_lc_name.get_text()
        lc_id_node = self.find_object(lc_name)
        if lc_id_node == None:
           lc_id_node = self.conf.create_new_object(lc_name)
        
        horn_node = self.check_and_create_sensor(self.dlg_horn.get_text())
        hb_node = self.check_and_create_sensor(self.dlg_heartbeat.get_text())
        hr_node = self.check_and_create_sensor(self.dlg_hornreset.get_text())
        c_node = self.check_and_create_sensor(self.dlg_confirm.get_text())
        
        # создаём три псевдо-горна (для орнажевого, красного и зелёного)
        self.check_and_create_sensors(lc_name,"Horn",3)
        # создаём лампочки (по количеству на колонке)
        self.check_and_create_sensors(lc_name,"Lamp",self.dlg_lc_count.get_value_as_int())
        
        # создаём очередной настроечный узел в <setting>
        lc_node = self.setnode.newChild(None,"LCAPS",None)
        o_node = lc_node.newChild(None,"orange",None)
        r_node = lc_node.newChild(None,"red",None)
        g_node = lc_node.newChild(None,"green",None)
        
        lc_node.setProp("name",lc_name)
        lc_node.setProp("heartbeat_max","10")
        lc_node.setProp("heartbeat",self.dlg_heartbeat.get_text())
        lc_node.setProp("horn",self.dlg_horn.get_text())
        lc_node.setProp("hornreset",self.dlg_hornreset.get_text())
        lc_node.setProp("confirm",self.dlg_confirm.get_text())
        
        lc_params = dict()
        lc_params['name'] = lc_name
        lc_params['xmlnode'] = lc_node
        lc_params['list'] = []
        lc_params['horn'] = horn_node
        lc_params['hornreset'] = hr_node
        lc_params['confirm'] = c_node
        lc_params['heartbeat_id'] = hb_node
        lc_params['heartbeat_max'] = "10"
        lc_params['orange'] = o_node
        lc_params['red'] = r_node
        lc_params['green'] = g_node
               
        self.lc_list[lc_name] = lc_params
        self.save_lclist_2xml()
        
        self.model.clear()
        self.build_lcaps_tree()
        self.conf.mark_changes()
    
    def check_and_create_sensor(self,name):
        node = self.find_sensor(name)
        if node == None:
           node = self.conf.create_new_sensor(name)
        return node        
        
    def check_and_create_sensors(self,lc_name,postfix,num):
        l_list=[]
        for i in range(1,num+1):
            l_list.append(str("%s_%s%d_C")%(lc_name,postfix,i))
        
        for i in l_list:
            node = self.find_sensor(i)
            if node == None:
               print "(CREATE NEW SENSOR): " + i
               node = self.conf.create_new_sensor(i)
    
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
        o = self.conf.o_dlg().run(self)
        if o != None:
           self.lcaps_dlg_lc_name.set_text(o.prop("name"))
    
    def on_lcaps_dlg_btn_heartbeat_clicked(self, button):
        print "***** heartbeat clicked**"
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_heartbeat.set_text(s.prop("name"))
    
    def on_lcaps_dlg_btn_horn_clicked(self, button):
        print "***** horn clicked**"
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_horn.set_text(s.prop("name"))
    
    def on_lcaps_dlg_btn_hornreset_clicked(self, button):
        print "***** hornreset clicked**"
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_hornreset.set_text(s.prop("name"))
    
    def on_lcaps_dlg_btn_confirm_clicked(self, button):
        print "***** confirm clicked**"
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_confirm.set_text(s.prop("name"))
      
     