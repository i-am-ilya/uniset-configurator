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
   tname = 6
   etype = 7
   xmlnode = 8
   s_xmlnode = 9
   l_xmlnode = 10
   maxnum = 11

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
        column = gtk.TreeViewColumn(_("Без\nзвука"), renderer,text=fid.nohorn)
        column.set_clickable(False)
        self.append_column(column)
        column = gtk.TreeViewColumn(_("Без\nквитирования"), renderer,text=fid.noconfirm)
        column.set_clickable(False)
        self.append_column(column)
        
        column = gtk.TreeViewColumn(_("Текстовое имя"), renderer,text=fid.tname)
        column.set_clickable(False)
        self.append_column(column)                
        
        
        self.lc_params=[ \
            ["dlg_lc","lcaps_dlg_lc",None,True], \
            ["lcaps_popup","lcaps_popup",None,True], \
            ["item_popup","lcaps_item_popup",None,True], \
            ["dlg_id_select_box","lcaps_id_select_box",None,True], \
            ["dlg_lc_name","lcaps_dlg_name","name",False], \
            ["dlg_lc_comm","lcaps_dlg_comm","comment",False], \
            ["dlg_horn","lcaps_dlg_horn","horn",False], \
            ["dlg_hornreset","lcaps_dlg_hornreset","hornreset",False], \
            ["dlg_confirm","lcaps_dlg_confirm","confirm",False], \
            ["dlg_lc_count","lcaps_dlg_lc_count","lamps",False], \
            ["dlg_heartbeat","lcaps_dlg_heartbeat","heartbeat",False], \
            ["dlg_heartbeat_max","lcaps_dlg_heartbeat_max","heartbeat_max",False] \
        ]
        self.init_glade_elements(self.lc_params) 
        
        self.lc_rm_params=[\
            ["dlg_rm","lcaps_dlg_remove",None,True], \
            ["rm_id","lcaps_rm_id",None,True], \
            ["rm_lamps","lcaps_rm_lamps",None,True], \
            ["rm_helpers","lcaps_rm_helpsens",None,True], \
            ["rm_title","lcaps_dlg_rm_title",None,True] \
        ]                
        self.init_glade_elements(self.lc_rm_params) 
               
        self.item_params=[ \
            ["dlg_lcaps","lcaps_dlg",None,True], \
            ["dlg_lcaps_title","lcaps_dlg_title",None,True], \
            ["item_sensor","lcaps_dlg_sensor","name",False], \
            ["item_ltype","lcaps_dlg_flash",None,True], \
            ["item_lamp","lcaps_dlg_lamp","lamp",False], \
            ["item_horn","lcaps_dlg_cb_nohorn","nohorn",False], \
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
        
        self.flamp_sections = ['orange','red','green']
        
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
        self.reopen()
    
    def reopen(self):
        self.model.clear()
        self.load_lcaps_list()
        self.build_lcaps_tree()
        self.show_all()        
    
    def load_lcaps_list(self):
        self.settings_node = self.conf.xml.findNode(self.conf.xml.getDoc(),"settings")[0]
        if self.settings_node == None:
            print "(LCAPSEditor::build_lcaps_list): <settings> not found?!..."
            return
        
        node = self.conf.xml.firstNode(self.settings_node.children)
        while node != None:
            if node.name.upper() == "LCAPS":
               
               lname = get_str_val(node.prop("name"))
               if lname == "":
                  print '**** Unknown <LCAPS name="?"'
                  node = self.conf.xml.nextNode(node)
                  continue
               
               numlamps  = get_int_val(node.prop("lamps"))
                
               item_list = self.load_item_dict(node,"orange")
               item_list.update(self.load_item_dict(node,"red"))
               item_list.update(self.load_item_dict(node,"green"))
               
               self.add_unused_item(lname,item_list,numlamps)
               
               lc_params = dict()
               lc_params['name'] = lname
               lc_params['xmlnode'] = node
               lc_params['list'] = item_list
               lc_params['numlamps'] = get_int_val(node.prop("lamps"))
               
               for sec in self.flamp_sections:
                   fparams = self.flamp_params[sec].copy()
                   fnode = self.create_xmlnode_if_not_exist(sec,node,False)
                   fparams["node"] = fnode
                   fparams["xmlprop"] = self.read_xml_param(fnode,fparams["xmlproplist"])
                   
                   cnode = self.create_xmlnode_if_not_exist(fparams["comm_name"],node,False)
                   fparams["comm_node"] = cnode
                   fparams["comm_xmlprop"] = self.read_xml_param(cnode,fparams["comm_xmlproplist"])
                   lc_params[sec] = fparams
               
               hparams = self.comhorn.copy()
               hparams["node"] = self.create_xmlnode_if_not_exist("comhorn",node,False)
               hparams["xmlprop"] = self.read_xml_param( hparams["node"],self.comhorn["xmlproplist"] )
               lc_params["comhorn"] = hparams
               self.lc_list[lname] = lc_params

            
            node = self.conf.xml.nextNode(node)
    
    def save_lclist_2xml(self):
        
        for lc_name, lc in self.lc_list.items():
            lc_node = lc['xmlnode']
            
            for sec in self.flamp_sections:
                self.set_xml_properties(lc[sec]["node"],lc[sec]["xmlprop"])
                if lc["comhorn"]["node"] != None:
                   self.set_xml_properties(lc[sec]["comm_node"],lc[sec]["comm_xmlprop"])
            
            if lc["comhorn"]["node"] != None:
               self.set_xml_properties(lc["comhorn"]["node"],lc["comhorn"]["xmlprop"])

            self.set_xml_list(lc['list'],lc_name)

    def set_xml_properties(self,node, proplist):
        if node == None or proplist == None:
           return
        
        for key, val in proplist.items():
            node.setProp(key,val)

    def set_xml_list(self, lc_list,lc_name):
        for i in lc_list.values():
            i_node = i[fid.xmlnode]
            if i_node == None:
               continue
            nm = str(i[fid.name])
            if nm == "" or nm == None:
               i_node.unlinkNode()
               continue
            
            i_node.setProp("num",nm)
            if i[fid.s_xmlnode] != None:
                i_node.setProp("name",i[fid.s_xmlnode].prop("name"))
            else:
                i_node.setProp("name","")
            i_node.setProp("lamp",self.get_lamp_name(lc_name,i[fid.name]))
            i_node.setProp("nohorn",str(i[fid.nohorn]))
            i_node.setProp("noconfirm",str(i[fid.noconfirm]))
            i_node.setProp("delay",str(i[fid.delay]))

    def name_if_exist(self,node):
        if node == None:
           return ""
        return node.prop("name")
    
    def create_xmlnode_if_not_exist(self,name,parent,recur=True):
        rnode = self.conf.xml.firstNode(parent.children)
        node = self.conf.xml.findNode(rnode,name)[0]
        if node == None:
           node = parent.newChild(None,name,None)
        return node
  
    def create_xmlnode_if_not_exist_by_prop(self,propname,propvalue,parent,name,recur=True):
        rnode = self.conf.xml.firstNode(parent.children)
        node = self.conf.xml.findNode_byProp(rnode,propname,propvalue,recur)[0]
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
        ret = dict()
        if o_node == None:
           return ret
        
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
               lst[i] = i_add
    
    def read_item_param(self,xmlnode,l_name):
        p=[]
        for i in range(0,fid.maxnum):
            p.append(None)
        
        p[fid.name] = get_str_val(xmlnode.prop("num"))
        p[fid.flamp] = self.get_light_name(l_name)
        p[fid.nohorn] = str(get_int_val(xmlnode.prop("nohorn")))
        p[fid.noconfirm] = str(get_int_val(xmlnode.prop("noconfirm")))
        p[fid.delay] = str(get_int_val(xmlnode.prop("delay")))
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
        i_dict = self.lc_list
        sorted_keys = sorted(i_dict, key=lambda x: x)
        for i in sorted_keys:        
            self.build_lcaps_item(self.lc_list[i])
   
    def build_lcaps_item(self,lc):
        it1 = self.model.append(None,self.build_lc_param(lc))
        i_dict = lc['list']
        sorted_keys = sorted(i_dict, key=lambda x: int(x))
        for i in sorted_keys:
            # временный хак!
            i_dict[i][fid.name] = str(i_dict[i][fid.name])
            it2 = self.model.append(it1,i_dict[i])    
        return it1
    
    def build_lc_param(self,lc):
        p=[]
        for i in range(0,fid.maxnum):
            p.append(None)
        xmlnode = lc['xmlnode']
        p[fid.name] = lc['name']
        p[fid.sensor] = ""
        p[fid.flamp] = ""
        p[fid.nohorn] = ""
        p[fid.noconfirm] = ""
        p[fid.delay] = ""
        p[fid.etype] = "L"
        p[fid.xmlnode] = xmlnode
        p[fid.s_xmlnode] = None
        p[fid.l_xmlnode] = None
        if xmlnode != None:
           p[fid.tname] = get_str_val(xmlnode.prop("comment"))
        
        return p
    
    def update_item_param(self,iter,params):
        num = 0
        for p in params:
            self.model.set_value(iter,num,p)
            num += 1
    
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
               self.lcaps_edit(iter)
            elif t == "I":
               self.on_edit_item(iter)               
        
        return False
    
    def on_lcaps_item_edit(self,menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter:
           return	  
        self.on_edit_item(iter)
    
    def on_lcaps_item_remove(self,menuitem):
        (model, iter) = self.get_selection().get_selected()
        self.on_remove_item(iter)  
    
    def on_lcaps_add(self,menuitem):
        self.lcaps_edit(None)
    
    def lcaps_edit(self,iter):
        lc_node = UniXML.EmptyNode()
        addNew = True
        if iter != None:
           self.dlg_id_select_box.set_sensitive(False)
           lc_node = self.model.get_value(iter,fid.xmlnode)
           addNew = False
        else:
           self.dlg_id_select_box.set_sensitive(True)
        
        self.init_elements_value(self.lc_params,lc_node)
        
        while True:
           res = self.dlg_lc.run()
           self.dlg_lc.hide()
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
        hr_node = self.conf.check_and_create_sensor(self.dlg_hornreset.get_text(),"DI")
        c_node = self.conf.check_and_create_sensor(self.dlg_confirm.get_text(),"DI")
        numlamps = self.dlg_lc_count.get_value_as_int()
        hb_node = None
        if self.dlg_heartbeat.get_text() != "":
            hb_node = self.conf.check_and_create_sensor(self.dlg_heartbeat.get_text(),"AI")
       
        # создаём лампочки (по количеству на колонке)
        self.check_and_create_sensors(lc_name,"Lamp",numlamps,"AO")

        lc_node = self.create_xmlnode_if_not_exist_by_prop("name",lc_name,self.settings_node,"LCAPS",False)
        
        lc_node.setProp("lamps",str(numlamps))
        lc_node.setProp("comment",str(self.dlg_lc_comm.get_text()))
        
        lc_params = dict()
        if addNew == True:
           lc_params['name'] = lc_name
           lc_params['xmlnode'] = lc_node
           lc_params['list'] = dict()
           self.add_unused_item(lc_name,lc_params['list'],numlamps)
        else:
           lc_params = self.lc_list[lc_name]           
        
        lc_params['horn'] = horn_node
        lc_params['hornreset'] = hr_node
        lc_params['confirm'] = c_node
        lc_params['heartbeat_id'] = hb_node
        lc_params['heartbeat_max'] = self.dlg_heartbeat_max.get_value_as_int()
        
        h_postfix = self.comhorn["comm_idname"]
        num = 1
        for sec in self.flamp_sections:
            
            fname = lc_name+"_"+sec.upper()
            self.conf.check_and_create_object(fname)
            
            fparams = self.flamp_params[sec].copy()
            fnode = self.create_xmlnode_if_not_exist(sec,lc_node,False)
            fnode.setProp("name",fname)
            fparams["node"] = fnode
            fparams["name"] = fname
            
            h_name = str("%s%s%d_C"%(lc_name,h_postfix,num))
            n_horn = self.conf.check_and_create_sensor(h_name,"DO")
            fnode.setProp("horn1",h_name)
            
            f_name = str("%s_Flash%s_C"%(lc_name,sec.upper()))
            n_flash = self.conf.check_and_create_sensor(f_name,"DO")
            fnode.setProp("flamp",f_name)
            self.set_new_flamp_prop(fnode)
            
            fparams["xmlprop"] = self.read_xml_param(fnode,fparams["xmlproplist"])
            
            # comm flash section
            fc_node = self.create_xmlnode_if_not_exist(fparams["comm_name"],lc_node,False)
            fc_name = lc_name + "_" + fparams["comm_idname"] 
            self.conf.check_and_create_object(fc_name)
            fc_node.setProp("name",fc_name)
            fc_node.setProp("out",f_name)
            fc_node.setProp("iotype", n_flash.prop("iotype"))
            for i in range(1,4):
                i_name = str("%s_Flash%s%d_C"%(lc_name,sec.upper(),i))
                n = self.create_xmlnode_if_not_exist_by_prop("name",i_name,fc_node,"item",False)
                self.conf.check_and_create_sensor(i_name,n_flash.prop("iotype"))
            
            fparams["comm_node"] = fc_node
            fparams["comm_xmlprop"] = self.read_xml_param(fc_node,fparams["comm_xmlproplist"])
            
            lc_params[sec] = fparams
            num = num + 1
        
        # comm horn section
        hparams = self.comhorn.copy()
        hc_name = lc_name + hparams["comm_idname"] 
        self.conf.check_and_create_object(hc_name)
        hc_node = self.create_xmlnode_if_not_exist("comhorn",lc_node,False)
        hc_node.setProp("name",hc_name)
        hc_node.setProp("iotype",horn_node.prop("iotype"))
        hc_node.setProp("out",horn_node.prop("name"))
        hparams["node"] = hc_node
        hparams["xmlprop"] = self.read_xml_param(hc_node,self.comhorn["xmlproplist"] )
        h_num = len(self.flamp_sections) + 3
        for i in range(1,h_num):
            i_name = str("%s%s%d_C"%(lc_name,h_postfix,i))
            self.create_xmlnode_if_not_exist_by_prop("name",i_name,hc_node,"item",False)
            self.conf.check_and_create_sensor(i_name,horn_node.prop("iotype"))
        
        lc_params["comhorn"] = hparams
        
        self.lc_list[lc_name] = lc_params
        self.save2xml_elements_value(self.lc_params,lc_node)
        self.save_lclist_2xml()
        
        if addNew == True:
           self.build_lcaps_item(lc_params)
           self.conf.update_list()

        self.conf.mark_changes()
        
    
    def set_new_flamp_prop(self, node):
        #node.setProp("heartbeat_max",str(self.dlg_heartbeat_max.get_value_as_int()))
        #node.setProp("heartbeat",self.dlg_heartbeat.get_text())
        node.setProp("hornreset",self.dlg_hornreset.get_text())
        node.setProp("confirm",self.dlg_confirm.get_text())
     
    def check_and_create_sensors(self,lc_name,postfix,num,iotype):
        l_list=[]
        for i in range(1,num+1):
            l_list.append(str("%s_%s%d_C")%(lc_name,postfix,i))
        
        for i in l_list:
            node = self.conf.find_sensor(i)
            if node == None:
               node = self.conf.create_new_sensor(i)
               node.setProp("iotype",iotype)
     
    def remove_sensors(self,lc_name,postfix,num):
        l_list=[]
        for i in range(1,num+1):
            l_list.append(str("%s_%s%d_C")%(lc_name,postfix,i))
        
        for i in l_list:
            self.conf.remove_sensor(i)
     
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
        if not iter:
            return
        
        self.lcaps_edit(iter)
    
    def on_lcaps_remove(self,menuitem):
       (model, iter) = self.get_selection().get_selected()
       if not iter:
          return
       
       lc_node = model.get_value(iter,fid.xmlnode)
       lc_name = model.get_value(iter,fid.name)

       self.rm_id.set_active(True)
       self.rm_lamps.set_active(True)
       self.rm_helpers.set_active(True)
       self.rm_title.set_text( str("Удаление '%s'\n/ %s /"%(lc_name,get_str_val(lc_node.prop("comment")))) )
       res = self.dlg_rm.run()
       self.dlg_rm.hide()
       if res != dlg_RESPONSE_OK:
            return False
       
       lc = self.lc_list[lc_name]
       
       if self.rm_id.get_active() == True:
          self.conf.remove_object(lc_name)
          self.conf.remove_object(lc["comhorn"]["node"].prop("name"))
          for sec in self.flamp_sections:
             fparams = self.flamp_params[sec]
             fnode = fparams["node"]
             self.conf.remove_object(fnode.prop("name"))
             self.conf.remove_object(fparams["comm_node"].prop("name"))
       
       if self.rm_lamps.get_active() == True:
          self.remove_sensors(lc_name,"Lamp", get_int_val(lc_node.prop("lamps")))
       
       h_postfix = self.comhorn["comm_idname"]
       if self.rm_helpers.get_active() == True:
          h_num = len(self.flamp_sections) + 3
          for i in range(1,h_num):
            i_name = str("%s%s%d_C"%(lc_name,h_postfix,i))
            self.conf.remove_sensor(i_name)
          
          num = 1
          for sec in self.flamp_sections:
            h_name = str("%s%s%d_C"%(lc_name,h_postfix,num))
            self.conf.remove_sensor(h_name)
            f_name = str("%s_Flash%s_C"%(lc_name,sec.upper()))
            self.conf.remove_sensor(f_name)
            for i in range(1,4):
                i_name = str("%s_Flash%s%d_C"%(lc_name,sec.upper(),i))
                self.conf.remove_sensor(i_name)
            num = num+1
       
       lc_node.unlinkNode()
       self.lc_list.pop(lc_name)
       self.model.remove(iter)
       self.conf.update_list()
       self.conf.mark_changes()

    def on_edit_item(self,iter):
        
        if not iter:
          return
        
        t = self.model.get_value(iter,fid.etype)
        lc_iter = iter
        if t == "I":
           lc_iter = self.model.iter_parent(iter)
        elif t == "L":
           lc_iter = iter
           print "*** ELEMENT TYPE != 'I'"
           return           
        else:
           print "*** FAILED ELEMENT TYPE " + t
           return        
        
        lc_name = self.model.get_value(lc_iter,fid.name)
        lc_params = self.lc_list[lc_name]
        lc_node = lc_params['xmlnode']
        
        i_node = UniXML.EmptyNode()
        addNew = True
        xmlnode = self.model.get_value(iter,fid.xmlnode)
        if xmlnode != None:
           i_node = xmlnode
           addNew = False
        
        self.init_elements_value(self.item_params,i_node)
        if xmlnode:
           self.set_combobox_element(self.item_ltype,self.get_light_name(xmlnode.parent.name))
        else:
           self.set_combobox_element(self.item_ltype,"")
        
        while True:
           res = self.dlg_lcaps.run()
           self.dlg_lcaps.hide()
           if res != dlg_RESPONSE_OK:
               return
           
           if self.item_sensor.get_text() == "":
              dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,_("Не задан датчик. Удалить привязку?"))
              res = dlg.run()			 
#              dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,"Не задан датчик")
#              res = dlg.run()
              dlg.hide()
              if res == gtk.RESPONSE_YES:
                 self.remove_item(lc_iter,iter)
                 return
              continue
           
           if self.item_ltype.get_active_text() not in ["Оранжевый","Красный","Зелёный"]:
              dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,"Не выбран маячок")
              res = dlg.run()
              dlg.hide()
              continue
           
           break
        
        prev_flamp = self.model.get_value(iter,fid.flamp)
        l_type = self.item_ltype.get_active_text()
        flamp = None
        fparams = None
        
        if l_type == "Оранжевый":
           fparams = lc_params['orange']
           flamp = 'orange'
        elif l_type == "Красный":
           fparams = lc_params['red']
           flamp = 'red'
        elif l_type == "Зелёный":
           fparams = lc_params['green']
           flamp = 'green'
        
        l_node = fparams["node"]

        # если теперт данная лампочка относится к другому "маячку"
        # надо удалять узел в предыдущей секции
        if xmlnode != None and flamp != prev_flamp:
           xmlnode.unlinkNode()

        num = self.model.get_value(iter,fid.name)
        
        xmlnode = self.create_xmlnode_if_not_exist_by_prop("num",num,l_node,"item",False)
        
        # имя лампочки - генерируется
        lamp_name = self.get_lamp_name(lc_name,num)
        lamp_node = self.conf.check_and_create_sensor(lamp_name,"AO")
        self.item_lamp.set_text(lamp_name)
        xmlnode.setProp("lamptype",lamp_node.prop("iotype"))
        
        # обновляем xmlnode по параметрам в диалоге
        self.save2xml_elements_value(self.item_params,xmlnode)

#        self.model.set_value(iter,fid.noconfirm,xmlnode.prop("noconfirm"))
#        self.model.set_value(iter,fid.noconfirm,xmlnode.prop("nohorn"))

        p = self.read_item_param(xmlnode,l_node.name)
        lc_params['list'][int(num)] = p

        if addNew == True:
           it1 = self.model.insert_after(None,iter,p)
           self.set_cursor( self.model.get_path(it1) )
           self.model.remove(iter)
           self.update_item_param(it1,p)
        else:
           self.update_item_param(iter,p)
        
        self.conf.mark_changes()
    
    def on_remove_item(self,iter):
        if not iter:
           return
        
        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,_("Are you sure?"))
        res = dlg.run()
        dlg.hide()
        if res == gtk.RESPONSE_NO:
            return False        
        
        t = self.model.get_value(iter,fid.etype)
        lc_iter = iter
        if t == "I":
           lc_iter = self.model.iter_parent(iter)
        elif t == "L":
            print "*** failed remove 'item' but iter type is 'L' (can be 'I')"
#           lc_iter = iter
            return
        else:
           print "*** FAILED ELEMENT TYPE " + t
           return

        self.remove_item(lc_iter, iter)

    def remove_item(self, lc_iter, iter):
        lc_name = self.model.get_value(lc_iter,fid.name)
        lc_params = self.lc_list[lc_name]
        lc_node = lc_params['xmlnode']            

        num = get_int_val(self.model.get_value(iter,fid.name))
        p = self.get_default_item(lc_name,num)
        lc_params['list'][num] = p

        xmlnode = self.model.get_value(iter,fid.xmlnode)
        xmlnode.unlinkNode()

        it1 = self.model.insert_after(None,iter,p)
        self.set_cursor( self.model.get_path(it1) )
        self.model.remove(iter)
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
    
    def on_generate_test_clicked(self, button):
        pass



def create_module(conf):
    return LCAPSEditor(conf)

def module_name():
    return "LCAPS"
