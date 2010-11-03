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
            ["item_ltype","lcaps_dlg_flash",None,True], \
            ["item_lamp","lcaps_dlg_lamp","lamp",False], \
            ["item_horn","lcaps_dlg_cb_nohorn",None,True], \
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
        
        self.flamp_sections = ["orange","red","green","silent"]
        self.nohorn_sections = ["silent"]
        self.nocomm_sections = ["silent"]
        
        self.flamp_params = dict()
        for sec in self.flamp_sections:
            p = dict()
            p["comm_name"] = str(sec+'_comflash')
            p["comm_node"] = None
            p["comm_idname"] = str(sec.upper()+'_CommFlash')
            p["comm_xmlproplist"] = ["name","out","iotype"]
            p["comm_xmlprop"] = None
            p["xmlproplist"] = ["name","horn1","hornreset","confirm","heartbeat_id","heartbeat_max"]
            p["xmlprop"] = None
            self.flamp_params[sec] = p
        
        self.comhorn = dict()
        self.comhorn["comm_name"] = "comhorn"
        self.comhorn["comm_node"] = None
        self.comhorn["comm_idname"] = '_CommHorn'
        self.comhorn["xmlproplist"] = ["name","out","iotype"]
        self.comhorn["xmlprop"] = None
        
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
               numlamps  = get_int_val(node.prop("lamps"))

               item_list = self.load_item_dict(node,"orange")
               item_list.update(self.load_item_dict(node,"red"))
               item_list.update(self.load_item_dict(node,"green"))
               item_list.update(self.load_item_dict(node,"silent"))
               
               self.add_unused_item(lname,item_list,numlamps)
               
               lc_params = dict()
               lc_params['name'] = lname
               lc_params['xmlnode'] = node
               lc_params['list'] = item_list
               lc_params['numlamps'] = get_int_val(node.prop("lamps"))
               
               for sec in self.flamp_sections:
                   fparams = self.flamp_params[sec]
                   fnode = self.create_xmlnode_if_not_exist(sec,node)
                   fparams["node"] = fnode
                   fparams["xmlprop"] = self.read_xml_param(fnode,fparams["xmlproplist"])
                   
                   cnode = self.create_xmlnode_if_not_exist(fparams["comm_name"],node)
                   fparams["comm_node"] = cnode
                   fparams["comm_xmlprop"] = self.read_xml_param(cnode,fparams["comm_xmlproplist"])
                   lc_params[sec] = fparams
               
               hparams = self.comhorn
               hparams["node"] = self.create_xmlnode_if_not_exist("comhorn",node)
               hparams["xmlprop"] = self.read_xml_param( hparams["node"],self.comhorn["xmlproplist"] )
               lc_params["comhorn"] = hparams

               self.lc_list[lname] = lc_params
            
            node = self.conf.xml.nextNode(node)
    
    def save_lclist_2xml(self):
        
        for lc_name, lc in self.lc_list.items():
            lc_node = lc['xmlnode']
            
            for sec in self.flamp_sections:
#                for k, v in lc[sec].items():
#                    print "********* v(%s)[%s]): %s"%(sec,k,str(v))
                self.set_xml_properties(lc[sec]["node"],lc[sec]["xmlprop"])
                if lc["comhorn"]["node"] != None:
                   self.set_xml_properties(lc[sec]["comm_node"],lc[sec]["comm_xmlprop"])
            
            if lc["comhorn"]["node"] != None:
               self.set_xml_properties(lc["comhorn"]["node"],lc["comhorn"]["xmlprop"])
            
            for i in lc['list'].values():
                i_node = i[fid.xmlnode]
                if i_node == None:
                   continue
                
                i_node.setProp("num",i[fid.name])
                i_node.setProp("name",i[fid.sensor])
                i_node.setProp("lamp",self.get_lamp_name(lc_name,i[fid.name]))
                i_node.setProp("nohorn",str(i[fid.nohorn]))
                i_node.setProp("noconfirm",str(i[fid.noconfirm]))
                i_node.setProp("delay",str(i[fid.delay]))

    def set_xml_properties(self,node, proplist):
        if node == None or proplist == None:
           return
        
        for key, val in proplist.items():
            node.setProp(key,val)

    def name_if_exist(self,node):
        if node == None:
           return ""
        return node.prop("name")
    
    def create_xmlnode_if_not_exist(self,name,parent):
        node = self.conf.xml.findNode(parent,name)[0]
        if node == None:
           node = parent.newChild(None,name,None)
        return node
  
    def create_xmlnode_if_not_exist_by_prop(self,propname,propvalue,parent,name):
        node = self.conf.xml.findNode_byProp(parent,propname,propvalue)[0]
        if node == None:
           node = parent.newChild(None,name,None)
           node.setProp(propname,propvalue)
        return node    
    
    def init_sensor(self,xmlnode,prop):
        name = get_str_val(xmlnode.prop(prop))
        node = None
        if name != "":
           return self.conf.find_sensor(name)
        
    def load_item_dict(self, xmlnode,l_name):
        o_node = self.conf.xml.findNode(xmlnode,l_name)[0]
        if o_node == None:
           return []
        ret = dict()
        node = self.conf.xml.firstNode(o_node.children)
        while node != None:
            plist = self.read_item_param(node,l_name)
            ret[get_int_val(plist[fid.name])] = plist
            node = self.conf.xml.nextNode(node)
        
        return ret
    
    def add_unused_item(self,lc_name,lst, maxnum):
        for i in range(1,maxnum+1):
            if not lst.has_key(i):
               i_add = self.get_default_item(lc_name,i)
               lst[str(i)] = i_add
    
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
        p[fid.s_xmlnode] = self.conf.find_sensor(get_str_val(xmlnode.prop("name")))
        p[fid.l_xmlnode] = self.conf.find_sensor(get_str_val(xmlnode.prop("lamp")))
        
        if p[fid.s_xmlnode] != None:
           s_node = p[fid.s_xmlnode]
           p[fid.sensor] = str("(%s)(%s)%s" % (s_node.prop("id"),s_node.prop("name"),s_node.prop("textname")))
        else:
           p[fid.sensor] = get_str_val(xmlnode.prop("name"))

        return p
      
    def get_default_item(self,lc_name,num):
        p=[]
        for i in range(0,fid.maxnum):
            p.append(None)
        
        lampname = self.get_lamp_name(lc_name,num)
        p[fid.name] = get_str_val(num)
        p[fid.flamp] = ""
        p[fid.nohorn] = "0"
        p[fid.noconfirm] = "0"
        p[fid.delay] = "0"
        p[fid.etype] = "I"
        p[fid.xmlnode] = None
        p[fid.s_xmlnode] = None
        p[fid.l_xmlnode] = self.conf.find_sensor(lampname)
        p[fid.sensor] = ""
        return p
    
    def read_xml_param(self,xmlnode,proplist):
        plist = dict()
        for p in proplist:
            plist[p] = xmlnode.prop(p)

        return plist
     
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
    
    def build_lcaps_tree(self):
        #self.lc_list.sort()
        for key, lc in self.lc_list.items():
            it1 = self.model.append(None,self.build_lc_param(lc))
#            for i in lc['list'].values():
#                it2 = self.model.append(it1,i)
            i_dict = lc['list']
            sorted_keys = sorted(i_dict, key=lambda x: int(x))
            for i in sorted_keys:
                it2 = self.model.append(it1,i_dict[i])
    
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
            if not iter: 
               self.lcaps_popup.popup(None, None, None, event.button, event.time)
               return False
            
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
        (model, iter) = self.get_selection().get_selected()
        if not iter:
           return	  
        
        while True:
           res = self.dlg_lcaps.run()
           self.dlg_lcaps.hide()
           if res != dlg_RESPONSE_OK:
               return
           
           if self.item_sensor.get_text() == "":
              dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,"Не задан датчик")
              res = dlg.run()
              dlg.hide()
      
           break
        
        t = mode.get_value(iter,fid.etype)
        lc_iter = iter
        if t == "I":
           lc_iter = model.iter_parent(iter)
        elif t == "L":
           lc_iter = iter
        else:
           print "*** FAILED ELEMENT TYPE " + t
           return
        
        lc_name = model.get_value(lc_iter,fid.name)
        lc_params = self.lc_list[lc_name]
        lc_node = lc_params['xmlnode']
        
        l_type = self.item_ltype.get_active_text()
        l_node = None
        if l_type == "Orange":
           l_node = lc_params['orange']
        elif l_type == "Red":
           l_node = lc_params['red']
        elif l_type == "Green":
           l_node = lc_params['green']
        
        self.read_item_param(self,xmlnode,l_name)
    
    def on_lcaps_item_edit(self,menuitem):
        pass
    
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
        lc_id_node = self.conf.check_and_create_object(lc_name)
        
        horn_node = self.conf.check_and_create_sensor(self.dlg_horn.get_text(),"DO")
        hb_node = self.conf.check_and_create_sensor(self.dlg_heartbeat.get_text(),"AI")
        hr_node = self.conf.check_and_create_sensor(self.dlg_hornreset.get_text(),"DI")
        c_node = self.conf.check_and_create_sensor(self.dlg_confirm.get_text(),"DI")
        
        # создаём лампочки (по количеству на колонке)
        self.check_and_create_sensors(lc_name,"Lamp",self.dlg_lc_count.get_value_as_int())
       
        # создаём очередной настроечный узел в <setting>
        lc_node = self.setnode.newChild(None,"LCAPS",None)
        lc_node.setProp("name",lc_name)
        lc_node.setProp("lamps",str(self.dlg_lc_count.get_value_as_int()))
        
        lc_params = dict()
        lc_params['name'] = lc_name
        lc_params['xmlnode'] = lc_node
        lc_params['list'] = dict()
        lc_params['horn'] = horn_node
        lc_params['hornreset'] = hr_node
        lc_params['confirm'] = c_node
        lc_params['heartbeat_id'] = hb_node
        lc_params['heartbeat_max'] = "10"
        
        h_postfix = self.comhorn["comm_idname"]
        num = 1
        for sec in self.flamp_sections:
            
            fname = lc_name+"_"+sec.upper()
            self.conf.check_and_create_object(fname)
            
            fparams = self.flamp_params[sec]
            fnode = self.create_xmlnode_if_not_exist(sec,lc_node)
            fnode.setProp("name",fname)
            fparams["node"] = fnode
            fparams["name"] = fname
            
            h_name = str("%s%s%d_C"%(lc_name,h_postfix,num))
            n_horn = self.conf.check_and_create_sensor(h_name,"DO")
            
            if sec not in self.nohorn_sections:
               fnode.setProp("horn1",h_name)
            
            f_name = str("%s_Flash%s_C"%(lc_name,sec.upper()))
            n_flash = self.conf.check_and_create_sensor(f_name,"DO")
            fnode.setProp("flamp",f_name)
            self.set_new_flamp_prop(fnode)
            
            fparams["xmlprop"] = self.read_xml_param(fnode,fparams["xmlproplist"])
            
            if sec not in self.nocomm_sections:
               # comm flash section
               fc_node = self.create_xmlnode_if_not_exist(fparams["comm_name"],lc_node)
               fc_name = lc_name + "_" + fparams["comm_idname"] 
               self.conf.check_and_create_object(fc_name)
               fc_node.setProp("name",fc_name)
               fc_node.setProp("out",f_name)
               fc_node.setProp("iotype", n_flash.prop("iotype"))
               for i in range(1,4):
                   n = fc_node.newChild(None,"item",None)
                   i_name = str("%s_Flash%s%d_C"%(lc_name,sec.upper(),i))
                   n.setProp("name",i_name)
                   self.conf.check_and_create_sensor(i_name,n_flash.prop("iotype"))
               fparams["comm_node"] = fc_node
               fparams["comm_xmlprop"] = self.read_xml_param(fc_node,fparams["comm_xmlproplist"])
            else:
               fparams["comm_node"] = None
            
            lc_params[sec] = fparams
            num = num + 1
        
        # comm horn section
        hparams = self.comhorn
        hc_name = lc_name + hparams["comm_idname"] 
        self.conf.check_and_create_object(hc_name)
        hc_node = self.create_xmlnode_if_not_exist("comhorn",lc_node)
        hc_node.setProp("name",hc_name)
        hc_node.setProp("iotype",horn_node.prop("iotype"))
        hc_node.setProp("out",horn_node.prop("name"))
        hparams["node"] = hc_node
        hparams["xmlprop"] = self.read_xml_param(hc_node,self.comhorn["xmlproplist"] )
        h_num = len(self.flamp_sections) + 3
        for i in range(1,h_num):
            n = hc_node.newChild(None,"item",None)
            i_name = str("%s%s%d_C"%(lc_name,h_postfix,i))
            n.setProp("name",i_name)
            self.conf.check_and_create_sensor(i_name,horn_node.prop("iotype"))
        
        lc_params["comhorn"] = hparams
        
#        print "****** %s: %s"%(lc_name,str(lc_params))
        
        self.lc_list[lc_name] = lc_params
        self.save_lclist_2xml()
        
        self.model.clear()
        self.build_lcaps_tree()
        self.conf.mark_changes()
        self.conf.update_list()
    
    def set_new_flamp_prop(self, node):
        node.setProp("heartbeat_max","10")
        node.setProp("heartbeat",self.dlg_heartbeat.get_text())
        node.setProp("hornreset",self.dlg_hornreset.get_text())
        node.setProp("confirm",self.dlg_confirm.get_text())
     
    def check_and_create_sensors(self,lc_name,postfix,num):
        l_list=[]
        for i in range(1,num+1):
            l_list.append(str("%s_%s%d_C")%(lc_name,postfix,i))
        
        for i in l_list:
            node = self.conf.find_sensor(i)
            if node == None:
               node = self.conf.create_new_sensor(i)
    
    def check_and_create_objects(self,lc_name,postfix,num):
        l_list=[]
        for i in range(1,num+1):
            l_list.append(str("%s_%s%d_C")%(lc_name,postfix,i))
        
        for i in l_list:
            node = self.conf.find_object(i)
            if node == None:
               node = self.conf.create_new_object(i)
    
    def on_lcaps_edit(self,menuitem):
        (model, iter) = self.get_selection().get_selected()
        self.on_edit_lcaps(iter)
    
    def on_lcaps_remove(self,menuitem):
       (model, iter) = self.get_selection().get_selected()
       if not iter:
          return
    
    def on_edit_lcaps(self,lc_iter):
        print "***** edit lcaps: iter" + str(lc_iter)

    def on_edit_item(self,iter):
        
        if not iter:
          return

        xmlnode = self.model.get_value(iter,fid.xmlnode)
        if xmlnode != None:
           self.init_elements_value(self.item_params,xmlnode)
        
        while True:
           res = self.dlg_lcaps.run()
           self.dlg_lcaps.hide()
           if res != dlg_RESPONSE_OK:
               return
           
           if self.item_sensor.get_text() == "":
              dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,"Не задан датчик")
              res = dlg.run()
              dlg.hide()
              continue
           
           if self.item_ltype.get_active_text() not in ["Оранжевый","Красный","Зелёный"]:
              dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,"Не выбран маячок")
              res = dlg.run()
              dlg.hide()
              continue
           
           break
        
        t = self.model.get_value(iter,fid.etype)
        lc_iter = iter
        if t == "I":
           lc_iter = self.model.iter_parent(iter)
        elif t == "L":
           lc_iter = iter
        else:
           print "*** FAILED ELEMENT TYPE " + t
           return
        
        lc_name = self.model.get_value(lc_iter,fid.name)
        lc_params = self.lc_list[lc_name]
        lc_node = lc_params['xmlnode']
        
        
        l_type = self.item_ltype.get_active_text()
        fparams = None
        if l_type == "Оранжевый":
           fparams = lc_params['orange']
        elif l_type == "Красный":
           fparams = lc_params['red']
        elif l_type == "Зелёный":
           fparams = lc_params['green']
        
        l_node = fparams["node"]
        
        num = self.model.get_value(iter,fid.name)
        xmlnode = self.create_xmlnode_if_not_exist_by_prop("num",num,l_node,"item")
#       xmlnode.setProp("num",num)
        # имя лампочки - генерируется
        self.item_lamp.set_text(self.get_lamp_name(lc_name,num)) 

        # обновляем xmlnode по параметрам в диалоге
        self.save2xml_elements_value(self.item_params,xmlnode)

        print "****** add: " + str(xmlnode)

        self.read_item_param(xmlnode,lc_name)
        self.conf.mark_changes()        
    
    def on_lcpas_dlg_btn_lamp_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.item_lamp.set_text(s.prop("name"))
    
    def on_lcpas_dlg_btn_sensor_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.item_sensor.set_text(s.prop("name"))
     
    def on_lcaps_dlg_id_sel_clicked(self, button):
        o = self.conf.o_dlg().run(self)
        if o != None:
           self.lcaps_dlg_lc_name.set_text(o.prop("name"))
    
    def on_lcaps_dlg_btn_heartbeat_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_heartbeat.set_text(s.prop("name"))
    
    def on_lcaps_dlg_btn_horn_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_horn.set_text(s.prop("name"))
    
    def on_lcaps_dlg_btn_hornreset_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_hornreset.set_text(s.prop("name"))
    
    def on_lcaps_dlg_btn_confirm_clicked(self, button):
        s = self.conf.s_dlg().run(self)
        if s != None:
           self.dlg_confirm.set_text(s.prop("name"))
     