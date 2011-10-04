# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_editor
import can_conf
from global_conf import *

# field id
class fid():
   name = 0
   param = 1
   can_xmlnode = 2
   etype = 3
   node_xmlnode = 4
   pic = 5
   maxnum = 6

pic_NET = 'can-net.png'
pic_NODE = 'node.png'  


class CANEditor(base_editor.BaseEditor, gtk.TreeView):

    def __init__(self, conf):
        
        gtk.TreeView.__init__(self)
        base_editor.BaseEditor.__init__(self,conf)
        
        self.can_conf = can_conf.CANConfig(conf.xml,conf.datdir)

        self.glade = gtk.glade.XML(conf.datdir+"can.glade")
        self.glade.signal_autoconnect(self)
        
        n_editor = conf.n_editor()
        if n_editor != None:
            n_editor.connect("change-node",self.nodeslist_change)
            n_editor.connect("add-new-node",self.nodeslist_add)
            n_editor.connect("remove-node",self.nodeslist_remove)        
        
        self.netlist = [] # list of pair [name,tree iter]

        self.model = None
        self.modelfilter = None
        #                          Name | Parameters | can_xmlnode | element type | node_xmlnode
        self.model = gtk.TreeStore(gobject.TYPE_STRING, # name
                                   gobject.TYPE_STRING, # parameters
                                   object,              # can xmlnode
                                   gobject.TYPE_STRING, # element type
                                   object,              # node xmlnode
                                   gtk.gdk.Pixbuf)      # picture
        self.modelfilter = self.model.filter_new()

        # create treeview
        self.set_model(self.model)
        self.set_rules_hint(True)
        self.connect("button-press-event", self.on_button_press_event)

        column = gtk.TreeViewColumn(_("Net name"))
        nmcell = gtk.CellRendererText()
        pbcell = gtk.CellRendererPixbuf()
        column.pack_start(pbcell, False)
        column.pack_start(nmcell, False)
        column.set_attributes(pbcell,pixbuf=fid.pic)
        column.set_attributes(nmcell,text=fid.name)
        column.set_clickable(False)
        self.append_column(column)
        
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Parameters"), renderer, text=fid.param)
        column.set_clickable(False)
        self.append_column(column)

        # expand all rows after the treeview widget has been realized
#       self.connect('realize', lambda tv: tv.expand_all())
        
        self.menu_list = [ \
            ["empty_popup","can_empty_popup",None,True], \
            ["net_popup","can_net_popup",None,True], \
            ["node_popup","can_node_popup",None,True] \
        ]
        self.init_glade_elements(self.menu_list,self.glade)
        
        self.net_param_list = [ \
            ["dlg_net","can_dlg_net",None,True], \
            ["net_name","can_net_name","net",False], \
            ["net_comm","can_net_comm","comment",False], \
            ["net_btnOK","can_net_btnOK",None,True], \
            ["net_btnCancel","can_net_btnCancel",None,True] \
        ]
        self.init_glade_elements(self.net_param_list,self.glade)

        self.node_param_list = [ \
            ["dlg_node","can_dlg_node",None,True], \
            ["dlg_card_btn","can_card1_btn",None,True], \
            ["dlg_card_box","can_card1_box",None,True], \
            ["dlg_card_param","can_card1_param",None,True], \
            ["node_name","can_lbl_nodename",None,True], \
            ["node_id","can_node_id","nodeID",False], \
            ["eds","can_eds","eds",False], \
            ["hbsensor","can_hb_sensor","hbSensor",False], \
            ["btn_hbsensor","can_btn_hbsensor",None,True], \
            ["respond","can_respond","respond",False], \
            ["btn_respond","can_btn_respond",None,True], \
            ["respond1","can_respond1","respond1",False], \
            ["btn_respond1","can_btn_respond1",None,True], \
            ["respond2","can_respond2","respond2",False], \
            ["btn_respond2","can_btn_respond2",None,True] \
        ]
        self.init_glade_elements(self.node_param_list,self.glade)

        self.dlg_card = gtk.combo_box_new_text()
        self.dlg_card.connect("changed", self.on_can_card_changed)

        self.dlg_card_box.add(self.dlg_card)
        self.edit_xmlnode = None

        self.dlg_card.show()
        self.cardinfo = dict()
        self.card_first_iter = None
        self.build_cards_list()
        
        self.reopen()
        self.show_all()
    
    def reopen(self):
        self.model.clear()
        self.netlist = []
        self.build_tree()
        self.edit_xmlnode = None    
    
    def build_tree(self):
        node = self.conf.xml.findNode(self.conf.xml.getDoc(),"nodes")[0].children.next 
        while node != None:
             cannode = self.conf.xml.findMyLevel(node.children,"can")
             cnode = None
             if cannode[0] != None:
                 cnode = cannode[0].children.next
             while cnode != None:
                   self.add_net(cnode,node)
                   cnode = self.conf.xml.nextNode(cnode)

             node = self.conf.xml.nextNode(node)
    
    def add_net(self,cannode, node):
         img = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_NET)
         name = cannode.prop("net")
         for n in self.netlist:
               if n[0] == name:
                    self.add_node(cannode,node,n[1])
                    return False
         
         iter = self.model.append(None,[name,to_str(cannode.prop("comment")),None,"net",None,img])
         self.netlist.append([name,iter,cannode.prop("comment")])
         self.add_node(cannode,node,iter)
         return True

    def add_node(self,cannode,node,iter):
         img = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_NODE)
         info  = self.get_can_info(cannode)
         return self.model.append(iter,[node.prop("name"),info,cannode,"node",node,img])

    def build_cards_list(self):
        model = self.dlg_card.get_model()
        self.card_first_iter = model.append( ["None"] )
        for k,c in self.can_conf.cards.items():
            it = model.append( [c["textname"]] )
            e = dict()
            e["iter"] = it
            e["key"] = k
            e["tname"] = c["textname"]
            dlg = self.glade.get_widget( str("can_dlg_" + c["name"]) )
            e["dlg"] =dlg
            
            self.cardinfo[c["name"]] = e
    
    def on_button_press_event(self, object, event):                                                                                                                                 
#        print "*** on_button_press_event"
        (model, iter) = self.get_selection().get_selected()

        if event.button == 3:                                                                                                                                                       
            if not iter: 
                 self.empty_popup.popup(None, None, None, event.button, event.time)
                 return False
            
            t = model.get_value(iter,fid.etype)
            if t == "net":
                self.net_popup.popup(None, None, None, event.button, event.time)
                return False                                                                                                                                                         
            if t == "node":
                self.node_popup.popup(None, None, None, event.button, event.time)
                return False

        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            if not iter:                                                                                                                                                                
                 return False
            else :
                 t = model.get_value(iter,fid.etype)
                 if t == "net": 
                     self.on_rename_net_activate(None)
                 elif t == "node":
                     self.on_edit_node_activate(None)
        return False

    def on_add_net_activate(self, menuitem):
        self.net_name.set_text("")
        res = self.dlg_net.run()
        self.dlg_net.hide()
        if res != dlg_RESPONSE_OK:
            return

        img = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_NET)
        name = self.net_name.get_text()
        comm = self.net_comm.get_text()
        iter = self.model.append(None,[name,comm,None,"net",None,img])
        self.netlist.append([name,iter,comm])
        self.conf.mark_changes()
        self.get_selection().select_iter(iter)
        self.on_add_node_activate(menuitem)
        
    def on_remove_net_activate(self, menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return
        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,_("Are you sure?"))
        res = dlg.run()
        dlg.hide()
        if res != gtk.RESPONSE_YES:
            return
        
        it = self.model.iter_children(iter)
        while it is not None:                     
            node = self.model.get_value(it,fid.can_xmlnode)
            node.unlinkNode()    
            it = self.model.iter_next(it)	  
        self.model.remove(iter)        
        self.conf.mark_changes()

    def check_node( self, node, rootiter ):
       it = self.model.iter_children(rootiter)
       while it is not None:                     
           if self.model.get_value(it,fid.node_xmlnode) == node:
               return it
           it = self.model.iter_next(it)           
       
       return None     

    def check_nodeID( self, nodeID, rootiter ):
       if nodeID == 0:
           return None

       it = self.model.iter_children(rootiter)
       while it is not None:
           n = self.model.get_value(it,fid.can_xmlnode).prop("nodeID")
           if n!="" and n!=None and int(eval(n)) == nodeID:
               return it
           it = self.model.iter_next(it)           
       
       return None     

    def on_add_node_activate(self, menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return
       
        while True:
            node = self.conf.n_dlg().run(self,None)
            if node == None:
                return
        
            etype = model.get_value(iter,fid.etype)
            rootiter=iter
            if etype == "node":
                rootiter = self.model.iter_parent(iter)
        
            if self.check_node(node,rootiter) != None:
                msg = "'" + node.prop("name") + "' " + _("already added!") 
                dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
                res = dlg.run()
                dlg.hide()
                continue
            break
        
        cnode = self.conf.xml.findMyLevel(node.children,"can")[0]
        if cnode == None:
            cnode = node.newChild(None,"can",None)
            if cnode == None:
               print "************** FAILED CREATE <can> for " + str(node.prop("name"))
               return        

        n = cnode.newChild(None,"item",None)
        n.setProp("net", self.model.get_value(rootiter,0))
        n.setProp("comment", self.model.get_value(rootiter,1))
        it = self.add_node(n,node,rootiter)
        self.edit_node(it)
        self.conf.mark_changes()

    def on_remove_node_activate(self, menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return
        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,_("Are you sure?"))
        res = dlg.run()
        dlg.hide()
        if res != gtk.RESPONSE_YES:
            return

        node = self.model.get_value(iter,fid.can_xmlnode)
        node.unlinkNode()
        self.model.remove(iter)
        self.conf.mark_changes()

    def on_rename_net_activate(self, menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return
        
        self.net_name.set_text(model.get_value(iter,fid.name))
        self.net_comm.set_text(model.get_value(iter,fid.param))
        res = self.dlg_net.run()
        self.dlg_net.hide()
        if res != dlg_RESPONSE_OK:
            return
        new_name = self.net_name.get_text()
        new_comm = self.net_comm.get_text()
        self.model.set_value(iter,fid.name,new_name)
        self.model.set_value(iter,fid.param,new_comm)

        it = self.model.iter_children(iter)
        while it is not None:                     
            node = self.model.get_value(it,fid.can_xmlnode)
            node.setProp("net",new_name)
            node.setProp("comment",new_comm)
            it = self.model.iter_next(it)	  
        
        self.conf.mark_changes()

    def init_text_param(self,node,pname):
        t = node.prop(pname)
        if t == None:
            return ""
        return t
    
    def on_btn_sensor_activate(self,btn):
        # т.к. функция универсальная для всех копок привязки к датчику
        # то для универсальности, обработку сделал через список пар "кнопка-label"
        lst = [ \
               [self.btn_respond,self.respond], \
               [self.btn_respond1,self.respond1], \
               [self.btn_respond2,self.respond2], \
               [self.btn_hbsensor,self.hbsensor] \
              ]
        
        lbl = None
        for v in lst:
            if v[0] == btn:
               lbl = v[1]
               break
        
        if lbl != None:
            self.conf.s_dlg().set_selected_name(lbl.get_text())
        
        s = self.conf.s_dlg().run(self)
        if s != None:
            lbl.set_text(to_str(s.prop("name")))
        else:
            lbl.set_text("")
        self.conf.mark_changes()            
    
    def on_edit_node_activate(self, menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return
        self.edit_node(iter)

    def set_card_type(self,cnode):
        ctype = cnode.prop("card")
        if ctype in self.cardinfo:
           self.dlg_card.set_active_iter( self.cardinfo[ctype]["iter"] )
        else:
           self.dlg_card.set_active_iter(self.card_first_iter)
    
    def get_card_by_name(self,tname):
        for k,c in self.cardinfo.items():
            if c["tname"] == tname:
               return self.can_conf.cards[c["key"]]
        return None
    
    def get_cardinfo_by_name(self,tname):
        for k,c in self.cardinfo.items():
            if c["tname"] == tname:
               return c
        return None
    
    def get_cardinfo_by_cnode(self,cnode):
        ctype = cnode.prop("card")
        if ctype in self.cardinfo:
           return self.cardinfo[ctype]
    
    def edit_node(self, iter):
        cnode = self.model.get_value(iter,fid.can_xmlnode)
        node_xmlnode = self.model.get_value(iter,fid.node_xmlnode)
        
        #print "xmlnode: " + str(cnode)
       
        self.node_name.set_text(node_xmlnode.prop("name"))
        self.init_elements_value(self.node_param_list,cnode)
        self.set_card_type(cnode)
        self.dlg_card_param.set_text( to_str(cnode.prop("module_param")) )
#       self.setup_dlg(cnode)
        self.edit_xmlnode = cnode
        self.can_param_is_correct = False
        cname = self.dlg_card.get_active_text()
        
        while True:
            res = self.dlg_node.run()
            self.dlg_node.hide()
            if res != dlg_RESPONSE_OK:
                return

            rootiter = self.model.iter_parent(iter) # NET level iterator
            nodeID = self.node_id.get_value_as_int()
            if nodeID != 0:
                it1 = self.check_nodeID(nodeID,rootiter)
                if it1 != None and self.model.get_value(it1,2) != cnode:
                    msg = "'" + str(nodeID) + "' " + _("already exist for %s") % self.model.get_value(it1,0)
                    dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
                    res = dlg.run()
                    dlg.hide()
                    continue
            
            if self.dlg_card.get_active_text() == "None" or (cname != self.dlg_card.get_active_text() \
                  and self.can_param_is_correct == False \
                  and self.dlg_card_param.get_text() == "" \
                  and self.dlg_card_btn.get_sensitive()):
               
               msg = "Не настроены параметры CAN"
               dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
               res = dlg.run()
               dlg.hide()
               continue
        
            break
        
        self.save2xml_elements_value(self.node_param_list,cnode)
        
        cinfo = self.get_card_by_name(self.dlg_card.get_active_text())
        cnode.setProp("card",cinfo["name"])
        cnode.setProp("module",cinfo["module"])
        cnode.setProp("module_param",self.dlg_card_param.get_text())
        
        print "xmlnode: " + str(cnode)
        
        self.model.set_value(iter,1,self.get_can_info(cnode))
        self.conf.mark_changes()
    
    def get_can_info(self,xmlnode):
        info  = 'nodeID=' + str(xmlnode.prop("nodeID"))
        info  = info + '; eds=' + str(xmlnode.prop("eds"))
        info  = info + ';...'
        return info
    
    def nodeslist_change(self,obj, xmlnode):
        # Ищем сети куда входит данный узел и обновляем info
        it = self.model.get_iter_first()
        while it is not None:
            # Идём по узлам
            it1 = self.model.iter_children(it)
            while it1 is not None:
                if self.model.get_value(it1,fid.node_xmlnode) == xmlnode:
                     self.model.set_value(it1,fid.name,xmlnode.prop("name"))
                     self.model.set_value(it1,fid.param,self.get_can_info(xmlnode))
                     self.conf.mark_changes()
                     break
                it1 = self.model.iter_next(it1)
            it = self.model.iter_next(it)        
    
    def nodeslist_add(self,obj, xmlnode):
        pass    
    
    def nodeslist_remove(self,obj, xmlnode):
        # Ищем сети куда входит данный узел и удаляем
        it = self.model.get_iter_first()
        while it is not None:
            # Идём по узлам
            it1 = self.model.iter_children(it)
            while it1 is not None:
                if self.model.get_value(it1,fid.node_xmlnode) == xmlnode:
#  Пока в редакторе не сделана настройка CAN по датчикам... это "вопрос" безполезен				  
#                    msg = _("Remove CAN configuration for sensors at node='") + str(xmlnode.prop("name")) + "'"
#                    dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,msg)
#                    res = dlg.run()
#                    dlg.hide()
#                    if res == gtk.RESPONSE_NO:
#                        return
                     self.model.remove(it1)
                     self.conf.mark_changes()
                     break
                it1 = self.model.iter_next(it1)
            
            it = self.model.iter_next(it)
    
    def on_can_card_changed(self,combobox):
        cinfo = self.get_cardinfo_by_name(self.dlg_card.get_active_text())
        if cinfo != None and cinfo["dlg"] != None:
           self.dlg_card_btn.set_sensitive(True)
        else:
           self.dlg_card_btn.set_sensitive(False)
           self.can_param_is_correct = True

    def on_can_card1_btn_clicked(self, button):
        cinfo = self.get_cardinfo_by_name(self.dlg_card.get_active_text())
        if cinfo and cinfo["dlg"] != None:
           cname = self.can_conf.cards[cinfo["key"]]["name"]
           if cname == "cpc108":
              self.can_param_is_correct = self.cpc108_config_dlg(cinfo,self.edit_xmlnode)
           elif cname == "can200mp":
              self.can_param_is_correct = self.can200mp_config_dlg(cinfo,self.edit_xmlnode)
           elif cname == "pci1680":
              self.can_param_is_correct = True
    
    def cpc108_config_dlg(self,cinfo,xmlnode):
        dlg = cinfo["dlg"]
        mmin = self.glade.get_widget( "can_cpc108_minminor" )
        mparam = self.glade.get_widget( "can_cpc108_param" )
        self.setup_cpc108_dlg(dlg,xmlnode)
        while True:
            res = dlg.run()
            dlg.hide()
            if res != dlg_RESPONSE_OK:
                self.dlg_card_param.set_text("")
                return False
            
            # проверка корректности...
            
            break
        
        mparam.set_text( "min_minor=" + str(mmin.get_value_as_int()) )
        self.dlg_card_param.set_text(mparam.get_text())
        return True

    def can200mp_config_dlg(self,cinfo,xmlnode):
        dlg = cinfo["dlg"]
        irq = self.glade.get_widget( "can_can200mp_irq" )
        ba1 = self.glade.get_widget( "can_can200mp_ba1" )
        ba2 = self.glade.get_widget( "can_can200mp_ba2" )
        mparam = self.glade.get_widget( "can_can200mp_param" )
        self.setup_can200mp_dlg(dlg,xmlnode)
        while True:
            res = dlg.run()
            dlg.hide()
            if res != dlg_RESPONSE_OK:
                self.dlg_card_param.set_text("")
                return False
            
            # проверка корректности...
            if irq.get_value_as_int() == 0:
               msg = "IRQ не может быть равен 0"
               wdlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
               res = wdlg.run()
               wdlg.hide()
               continue
            
            if ba1.get_text() == "" or ba2.get_text() == "":
               msg = "'Base adress' должен быть задан обязательно"
               wdlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
               res = wdlg.run()
               wdlg.hide()
               continue
            
            break
        
        s =  str("irq0=%d porta0=%s portb0=%s"%(irq.get_value_as_int(),ba1.get_text(),ba2.get_text()))
        mparam.set_text(s)
        self.dlg_card_param.set_text(s)
        return True
    
    def get_param_list(self,s_param):
        p = []
        
        if s_param == "" or s_param == None:
           return p
        
        l = s_param.split(" ")
        for s in l:
            v = s.split("=")
            if len(v) > 1:
               p.append([v[0],v[1]])
            else:
               print "(can.get_param_list:WARNING): (v=x) undefined value for " + str(s)
               p.append([v[0],""])
        return p
    
    def setup_cpc108_dlg(self,dlg,xmlnode):
        mparam = xmlnode.prop("module_param")
        plist = self.get_param_list(mparam)
        mmin = self.glade.get_widget( "can_cpc108_minminor" )
        for p in plist:
            if p[0] == "min_minor":
               mmin.set_value(int(p[1]))
        
    def setup_can200mp_dlg(self,dlg,xmlnode):
        mparam = xmlnode.prop("module_param")
        plist = self.get_param_list(mparam)
        irq = self.glade.get_widget( "can_can200mp_irq" )
        ba1 = self.glade.get_widget( "can_can200mp_ba1" )
        ba2 = self.glade.get_widget( "can_can200mp_ba2" )
        for p in plist:
            pname = p[0]
            if pname == "irq0":
               irq.set_value(int(p[1]))
            elif pname == "porta0":
               ba1.set_text(p[1])
            elif pname == "portb0":
               ba2.set_text(p[1])
    
def create_module(conf):
    return CANEditor(conf)

def module_name():
    return "CAN"
