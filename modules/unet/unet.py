# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_editor
from global_conf import *

# field id
class fid():
   name = 0
   param = 1
   unet_xmlnode = 2
   etype = 3
   node_xmlnode = 4
   pic = 5
   maxnum = 6

pic_NET = 'can-net.png'
pic_NODE = 'node.png'  
default_NET_NAME="Default"

class UNETEditor(base_editor.BaseEditor, gtk.TreeView):

    def __init__(self, conf):
        
        gtk.TreeView.__init__(self)
        base_editor.BaseEditor.__init__(self,conf)
        
        self.builder = gtk.Builder()
        self.builder.add_from_file(conf.datdir+"unet.ui")
        self.builder.connect_signals(self)
        
        n_editor = conf.n_editor()
        if n_editor != None:
            n_editor.connect("change-node",self.nodeslist_change)
            n_editor.connect("add-new-node",self.nodeslist_add)
            n_editor.connect("remove-node",self.nodeslist_remove)        
        
        self.netlist = [] # list of pair [name,tree iter]

        self.model = None
        self.modelfilter = None

        self.model = gtk.TreeStore(gobject.TYPE_STRING, # name
                                   gobject.TYPE_STRING, # parameters
                                   object,              # unet xmlnode
                                   gobject.TYPE_STRING, # element type
                                   object,              # node xmlnode
                                   gtk.gdk.Pixbuf)      # picture

        #self.modelfilter = self.model.filter_new()

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
        
        self.menu_list = [
            ["empty_popup","unet_empty_popup",None,True],
            ["net_popup","unet_net_popup",None,True],
            ["node_popup","unet_node_popup",None,True],
            ["mi_net_rename","unet_net_rename",None,True],
            ["mi_net_remove","unet_net_remove",None,True],
            ["mi_node_add","unet_node_add",None,True],
            ["mi_node_remove","unet_node_remove",None,True]
        ]
        self.init_builder_elements(self.menu_list,self.builder)
        
        self.net_param_list = [
            ["dlg_net","unet_dlg_net",None,True],
            ["net_name","unet_net_name","unet_net",False],
            ["net_comm","unet_net_comm","unet_comment",False],
            ["net_btnOK","unet_net_btnOK",None,True],
            ["net_btnCancel","unet_net_btnCancel",None,True]
        ]
        self.init_builder_elements(self.net_param_list,self.builder)

        self.node_param_list = [
            ["dlg_node","unet_dlg_node",None,True],
            ["node_name","unet_lbl_nodename",None,True],
            ["btn_respond","unet_btn_respond",None,True],
			["btn_respond1","unet_btn_respond1",None,True],
			["btn_respond2","unet_btn_respond2",None,True],
            ["respond","unet_respond","unet_respond_id",False],
            ["respond1","unet_respond1","unet_respond1_id",False],
            ["respond2","unet_respond2","unet_respond2_id",False],
            ["btn_lpsensor","unet_btn_lpsensor",None,True],
            ["btn_lpsensor1","unet_btn_lpsensor1",None,True],
            ["btn_lpsensor2","unet_btn_lpsensor2",None,True],
            ["lostpacket","unet_lpsensor","unet_lostpackets_id",False],
            ["lostpacket1","unet_lpsensor1","unet_lostpackets1_id",False],
            ["lostpacket2","unet_lpsensor2","unet_lostpackets2_id",False],
            ["btn_ignore","unet_cb_ignore","unet_ignore",False],
            ["btn_resp_invert","unet_cb_resp_invert","unet_respond_invert",False]
        ]
        self.init_builder_elements(self.node_param_list,self.builder)
#            ["hbsensor","unet_hb_sensor","hbSensor",False],
#            ["btn_hbsensor","unet_btn_hbsensor",None,True],

        # чтобы сделать функцию выбора привязки датчиков одной на все кнопки
        # то для универсальности, обработку делаем через список пар "кнопка-label"
        # см. on_btn_sensor_activate()
        self.btn_lst = [
               [self.btn_respond,self.respond],
               [self.btn_respond1,self.respond1],
               [self.btn_respond2,self.respond2],
               [self.btn_lpsensor,self.lostpacket],
               [self.btn_lpsensor1,self.lostpacket1],
               [self.btn_lpsensor2,self.lostpacket2]
              ]
#             [self.btn_hbsensor,self.hbsensor],

        self.edit_xmlnode = None
        self.default_list_it = None
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
             # пока не unet не предусматривает выделение отдельного тега <unet> внутри <node>
             #cannode = self.conf.xml.findMyLevel(node.children,"unet")
             #cnode = node
             #if cannode[0] != None:
             #    cnode = cannode[0].children.next
             #while cnode != None:
             #       self.add_net(cnode,node)
             #      cnode = self.conf.xml.nextNode(cnode)
             cnode = node
             self.add_net(cnode,node)

             node = self.conf.xml.nextNode(node)
    
    def add_net(self,cannode, node):
         img = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_NET)
         name = to_str(cannode.prop("unet"))
         if name == "":
            name=default_NET_NAME

         for n in self.netlist:
               if n[0] == name:
                    self.add_node(cannode,node,n[1])
                    return False

         iter = self.model.append(None,[name,to_str(cannode.prop("unet_comment")),None,"net",None,img])
         if name == default_NET_NAME:
            self.default_list_it = iter

         self.netlist.append([name,iter,to_str(cannode.prop("unet_comment"))])
         self.add_node(cannode,node,iter)
         return True

    def add_node(self,cannode,node,iter):
         img = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_NODE)
         info  = self.get_unet_info(cannode)
         return self.model.append(iter,[to_str(node.prop("name")),info,cannode,"node",node,img])

    def is_iter_equal(self, l_iter, r_iter):

        if not l_iter or not r_iter:
           return False

        return ( self.model.get_string_from_iter(l_iter) == self.model.get_string_from_iter(r_iter) )

    def on_button_press_event(self, object, event):                                                                                                                                 
#        print "*** on_button_press_event"
        (model, iter) = self.get_selection().get_selected()

        if event.button == 3:                                                                                                                                                       
            if not iter: 
                 self.empty_popup.popup(None, None, None, event.button, event.time)
                 return False

            t = model.get_value(iter,fid.etype)
            if t == "net":
                if self.is_iter_equal(iter,self.default_list_it):
                   self.mi_net_rename.set_sensitive(False)
                   self.mi_net_remove.set_sensitive(False)
                else:
                   self.mi_net_rename.set_sensitive(True)
                   self.mi_net_remove.set_sensitive(True)

                self.net_popup.popup(None, None, None, event.button, event.time)
                return False                                                                                                                                                         

            if t == "node":
               rootiter = model.iter_parent(iter)
               if self.is_iter_equal(rootiter,self.default_list_it):
                  self.mi_node_add.set_sensitive(False)
                  self.mi_node_remove.set_sensitive(False)
               else:
                  self.mi_node_add.set_sensitive(True)
                  self.mi_node_remove.set_sensitive(True)

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
                     self.on_node_edit_activate(None)
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
        self.on_node_add_activate(menuitem)
        
    def on_remove_net_activate(self, menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return

        if model.get_value(iter,0) == default_NET_NAME:
           msg = "Network '%s' can not be deleted..."%default_NET_NAME
           dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
           res = dlg.run()
           dlg.hide()
           return

        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,_("Are you sure?"))
        res = dlg.run()
        dlg.hide()
        if res != gtk.RESPONSE_YES:
            return
        
        it = self.model.iter_children(iter)
        while it is not None:                     
            self.remove_node(it)
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

    def find_defaultlist( self ):
        it = self.model.get_iter_first()
        def_it = None
        while it is not None:
            if self.model.get_value(it,0) == default_NET_NAME:
               def_it = it
               break;

            it = self.model.iter_next(it)

        return def_it

    def find_in_defaultlist( self, node ):
        def_it = self.find_defaultlist()
        if not def_it:
           return None

        # Идём по узлам
        it1 = self.model.iter_children(def_it)
        while it1 is not None:
            if self.model.get_value(it1,fid.node_xmlnode) == node:
               return it1

            it1 = self.model.iter_next(it1)

        return None

    def on_node_add_activate(self, menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return

        node = None
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

#        Оставлено на случай если для <unet> будет выделена отдельная подсекция в <node>        
#        cnode = self.conf.xml.findMyLevel(node.children,"unet")[0]
#        if cnode == None:
#            cnode = node.newChild(None,"unet",None)
#            if cnode == None:
#               print "************** FAILED CREATE <unet> for " + str(node.prop("name"))
#               return
#        n = cnode.newChild(None,"item",None)

#		Поэтому пока что свойства unet пишутся прямо в <node ...>
        n = node

        rm_iter = self.find_in_defaultlist(n)
        if rm_iter:
           self.model.remove(rm_iter)

        n.setProp("unet", model.get_value(rootiter,0))
        n.setProp("unet_comment", model.get_value(rootiter,1))
        it = self.add_node(n,node,rootiter)
        self.edit_node(it)
        self.conf.mark_changes()

    def on_node_remove_activate(self, menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return
        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,_("Are you sure?"))
        res = dlg.run()
        dlg.hide()
        if res != gtk.RESPONSE_YES:
            return

        node = self.model.get_value(iter,fid.unet_xmlnode)
        self.remove_node(iter)
        
    def remove_node(self,iter):

        node = self.model.get_value(iter,fid.unet_xmlnode)
        #node.unlinkNode()
        node.setProp("unet","")
        self.model.remove(iter)
        self.add_node(node,node,self.default_list_it)
        self.conf.mark_changes()

    def on_rename_net_activate(self, menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return

        if model.get_value(iter,0) == default_NET_NAME:
           msg = "Network '%s' can not be renamed..."%default_NET_NAME
           dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
           res = dlg.run()
           dlg.hide()
           return        

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
            node = self.model.get_value(it,fid.unet_xmlnode)
            node.setProp("unet",new_name)
            node.setProp("unet_comment",new_comm)
            it = self.model.iter_next(it)	  
        
        self.conf.mark_changes()

    def init_text_param(self,node,pname):
        t = node.prop(pname)
        if t == None:
            return ""
        return t
    
    def on_btn_sensor_activate(self,btn):
        lbl = None
        for v in self.btn_lst:
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
    
    def on_node_edit_activate(self, menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return
        self.edit_node(iter)

    def edit_node(self, iter):
        cnode = self.model.get_value(iter,fid.unet_xmlnode)
        node_xmlnode = self.model.get_value(iter,fid.node_xmlnode)
        
        #print "EDIT: xmlnode: " + str(cnode)
       
        self.node_name.set_text(node_xmlnode.prop("name"))
        self.init_elements_value(self.node_param_list,cnode)
        self.edit_xmlnode = cnode
        self.unet_param_is_correct = False
        
        while True:
            res = self.dlg_node.run()
            self.dlg_node.hide()
            if res != dlg_RESPONSE_OK:
                return

            rootiter = self.model.iter_parent(iter) # NET level iterator
            break
        
        self.save2xml_elements_value(self.node_param_list,cnode)

        self.model.set_value(iter,1,self.get_unet_info(cnode))
        self.conf.mark_changes()
    
    def get_unet_info(self,xmlnode):
        info  = ''
        if to_str(xmlnode.prop("unet_ignore")) != "":
           info = "**IGNORE=1!**"
        info  = "%s respond_id=%s, lostpackets_id=%s"%(info,to_str(xmlnode.prop("unet_respond_id")),
                 to_str(xmlnode.prop("unet_lostpackets_id")))
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
                     self.model.set_value(it1,fid.param,self.get_unet_info(xmlnode))
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
                     self.model.remove(it1)
                     self.conf.mark_changes()
                     break
                it1 = self.model.iter_next(it1)
            
            it = self.model.iter_next(it)
    
def create_module(conf):
    return UNETEditor(conf)

def module_name():
    return "UNET"
