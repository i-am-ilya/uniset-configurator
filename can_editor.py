# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_editor

class CANEditor(base_editor.BaseEditor):

    def __init__(self, conf):

        super(CANEditor, self).__init__(conf)
        conf.glade.signal_autoconnect(self)
        
        self.netlist = [] # list of pair [name,tree iter]

        self.model = None
        self.modelfilter = None
        #                          Name | Parameters | can_xmlnode | element type | node_xmlnode
        self.model = gtk.TreeStore(gobject.TYPE_STRING,gobject.TYPE_STRING,object,gobject.TYPE_STRING,object)
        self.modelfilter = self.model.filter_new()

        # create treeview
        self.set_model(self.model)
        self.set_rules_hint(True)
        self.connect("button-press-event", self.on_button_press_event)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Net name"), renderer, text=0)
        column.set_clickable(False)
        self.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Parameters"), renderer, text=1)
        column.set_clickable(False)
        self.append_column(column)

        # expand all rows after the treeview widget has been realized
#       self.connect('realize', lambda tv: tv.expand_all())
        
        self.menu_list = [ \
            ["empty_popup","can_empty_popup",None,True], \
            ["net_popup","can_net_popup",None,True], \
            ["node_popup","can_node_popup",None,True] \
        ]
        self.init_glade_elements(self.menu_list)
        
        self.build_tree()
        
        self.net_param_list = [ \
            ["dlg_net","can_dlg_net",None,True], \
            ["net_name","can_net_name","net",False], \
            ["net_comm","can_net_comm","comment",False], \
            ["net_btnOK","can_net_btnOK",None,True], \
            ["net_btnCancel","can_net_btnCancel",None,True] \
        ]
        self.init_glade_elements(self.net_param_list)

        self.node_param_list = [ \
            ["dlg_node","can_dlg_node",None,True], \
            ["node_name","can_lbl_nodename",None,True], \
            ["node_btnOK","can_node_btnOK",None,True], \
            ["node_btnCancel","can_node_btnCancel",None,True], \
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
        self.init_glade_elements(self.node_param_list)
      
        self.show_all()
       
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
         name = cannode.prop("net")
         for n in self.netlist:
               if n[0] == name:
                    self.add_node(cannode,node,n[1])
                    return False
         
         iter = self.model.append(None,[name,self.conf.get_str_val(cannode.prop("comment")),None,"net",None])
         self.netlist.append([name,iter,cannode.prop("comment")])
         self.add_node(cannode,node,iter)
         return True

    def add_node(self,cannode,node,iter):
         info  = 'nodeID=' + str(cannode.prop("nodeID"))
         info  = info + '; eds=' + str(cannode.prop("eds"))
         info  = info + ';...'
         return self.model.append(iter,[node.prop("name"),info,cannode,"node",node])

    def on_button_press_event(self, object, event):                                                                                                                                 
#        print "*** on_button_press_event"
        (model, iter) = self.get_selection().get_selected()

        if event.button == 3:                                                                                                                                                       
            if not iter: 
                 self.empty_popup.popup(None, None, None, event.button, event.time)
                 return False
            
            t = model.get_value(iter,3)
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
                 t = model.get_value(iter,3)
                 if t == "net": 
                     self.on_rename_net_activate(None)
                 elif t == "node":
                     self.on_edit_node_activate(None)
        return False

    def on_add_net_activate(self, menuitem):
        self.net_name.set_text("")
        res = self.dlg_net.run()
        self.dlg_net.hide()
        if res != gtk.RESPONSE_OK:
            return

        name = self.net_name.get_text()
        comm = self.net_comm.get_text()
        iter = self.model.append(None,[name,comm,None,"net",None])
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
        if res == gtk.RESPONSE_NO:
            return
        
        it = self.model.iter_children(iter)
        while it is not None:                     
            node = self.model.get_value(it,2)
            node.unlinkNode()    
            it = self.model.iter_next(it)	  
        self.model.remove(iter)        
        self.conf.mark_changes()

    def check_node( self, node, rootiter ):
       it = self.model.iter_children(rootiter)
       while it is not None:                     
           if self.model.get_value(it,4) == node:
               return it
           it = self.model.iter_next(it)           
       
       return None     

    def check_nodeID( self, nodeID, rootiter ):
       if nodeID == 0:
           return None

       it = self.model.iter_children(rootiter)
       while it is not None:
           n = self.model.get_value(it,2).prop("nodeID")
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
        
            etype = model.get_value(iter,3)
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
        if res == gtk.RESPONSE_NO:
            return

        node = self.model.get_value(iter,2)
        node.unlinkNode()
        self.model.remove(iter)
        self.conf.mark_changes()

    def on_rename_net_activate(self, menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return
        
        self.net_name.set_text(model.get_value(iter,0))
        self.net_comm.set_text(model.get_value(iter,1))
        res = self.dlg_net.run()
        self.dlg_net.hide()
        if res != gtk.RESPONSE_OK:
            return
        new_name = self.net_name.get_text()
        new_comm = self.net_comm.get_text()
        self.model.set_value(iter,0,new_name)
        self.model.set_value(iter,1,new_comm)

        it = self.model.iter_children(iter)
        while it is not None:                     
            node = self.model.get_value(it,2)
            node.setProp("net",new_name)
            node.setProp("comment",new_comm)
            it = self.model.iter_next(it)	  
        
        self.conf.mark_changes()

    def init_text_param(self,node,pname):
        t = node.prop(pname)
        if t == None:
            return ""
        return t
    
    def on_dlg_btn_clicked(self, btn):
        if btn == self.net_btnOK:
              self.dlg_net.response(gtk.RESPONSE_OK)
        elif btn == self.net_btnCancel:
              self.dlg_net.response(gtk.RESPONSE_CANCEL)
        elif btn == self.node_btnOK:
              self.dlg_node.response(gtk.RESPONSE_OK)
        elif btn == self.node_btnOK:
              self.dlg_node.response(gtk.RESPONSE_OK)
    
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
            lbl.set_text(self.conf.get_str_val(s.prop("name")))
        else:
            lbl.set_text("")
        self.conf.mark_changes()            
    
    def on_edit_node_activate(self, menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return
        self.edit_node(iter)

    def edit_node(self, iter): 
        cnode = self.model.get_value(iter,2) # can xmlnode
        node_xmlnode = self.model.get_value(iter,4) # node xmlnode
       
        self.node_name.set_text(node_xmlnode.prop("name"))
        self.init_elements_value(self.node_param_list,cnode)

        while True:
            res = self.dlg_node.run()
            self.dlg_node.hide()
            if res != gtk.RESPONSE_OK:
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
            break
        
        self.save2xml_elements_value(self.node_param_list,cnode)
        info  = 'nodeID=' + str(cnode.prop("nodeID"))
        info  = info + '; eds=' + str(cnode.prop("eds"))
        info  = info + ';...'
        self.model.set_value(iter,1,info)
        self.conf.mark_changes()
