# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure

class CANMain(gtk.TreeView):

    xml = None

    def __init__(self, conf):

        self.conf = conf
        self.netlist = [] # list of pair [name,tree iter]

        gtk.TreeView.__init__(self)
        self.model = None
        self.modelfilter = None
        #                          Name | Parameters | can_xmlnode | element type | parent iterator | node_xmlnode
        self.model = gtk.TreeStore(gobject.TYPE_STRING,gobject.TYPE_STRING,object,gobject.TYPE_STRING,object,object)
        self.modelfilter = self.model.filter_new()

        # create treeview
        self.set_model(self.model)
        self.set_rules_hint(True)
        self.connect("button-press-event", self.on_button_press_event)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Name"), renderer, text=0)
        column.set_clickable(False)
        self.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Parameters"), renderer, text=1)
        column.set_clickable(False)
        self.append_column(column)

        # expand all rows after the treeview widget has been realized
#       self.connect('realize', lambda tv: tv.expand_all())

        self.net_popup = gtk.Menu() 
        i0 = gtk.MenuItem( _("add new network") ) 
        i0.connect("activate", self.on_add_net_activate)
        i0.show() 
        self.net_popup.append(i0) 
        i1 = gtk.MenuItem( _("remove network") ) 
        i1.connect("activate", self.on_remove_net_activate)
        i1.show() 
        self.net_popup.append(i1) 
        
        i5 = gtk.MenuItem( _("add new node") ) 
        i5.connect("activate", self.on_add_node_activate)
        i5.show() 
        self.net_popup.append(i5) 

        self.node_popup = gtk.Menu() 
        i2 = gtk.MenuItem( _("edit node") ) 
        i2.connect("activate", self.on_edit_node_activate)
        i2.show() 
        self.node_popup.append(i2)
        i3 = gtk.MenuItem( _("add new node") ) 
        i3.connect("activate", self.on_add_node_activate)
        i3.show() 
        self.node_popup.append(i3) 
        i4 = gtk.MenuItem( _("remove node") ) 
        i4.connect("activate", self.on_remove_node_activate)
        i4.show() 
        self.node_popup.append(i4) 

        self.build_tree()

        vb = gtk.VBox()
        hb = gtk.HBox()

        # node label
        self.node_name = gtk.Label()
        self.node_name.show()
        vb.pack_start(self.node_name,True,True,3)

        lb1 = gtk.Label(_("NodeID: "))
        lb1.show()
        self.node_id = gtk.Entry()
        self.node_id.set_width_chars(5)
        self.node_id.set_max_length(8)
        self.node_id.show()
        hb1 = gtk.HBox()
        hb1.pack_start(lb1,False,False,3)
        hb1.pack_start(self.node_id,True,True,3)
        hb1.show()
        vb.pack_start(hb1,True,True,3)

        lb11 = gtk.Label(_("eds file: "))
        lb11.show()
        self.eds = gtk.Entry()
        self.eds.set_width_chars(20)
        self.eds.set_max_length(80)
        self.eds.show()
        hb2 = gtk.HBox()
        hb2.pack_start(lb11,False,False,3)
        hb2.pack_start(self.eds,True,True,3)
        hb2.show()
        vb.pack_start(hb2,True,True,3)

        lbl2 = gtk.Label(_("hbSensor: "))
        lbl2.show()
        self.hb_sensor = gtk.Label()
        self.hb_sensor.show()
        self.btn_sel_hbsensor = gtk.Button("...")
        self.btn_sel_hbsensor.connect("clicked", self.on_sensor_select)
        self.btn_sel_hbsensor.show()
        hb3 = gtk.HBox()
        hb3.pack_start(lbl2,False,False,3)
        hb3.pack_start(self.hb_sensor,True,True,3)
        hb3.pack_start(self.btn_sel_hbsensor,False,False,3)
        hb3.show()
        vb.pack_start(hb3,True,True,3)

        lbl4 = gtk.Label(_("NodeRespond: "))
        lbl4.show()
        self.respond = gtk.Label()
        self.respond.show()
        self.btn_respond = gtk.Button("...")
        self.btn_respond.connect("clicked", self.on_sensor_select)
        self.btn_respond.show()
        hb4 = gtk.HBox()
        hb4.pack_start(lbl4,False,False,3)
        hb4.pack_start(self.respond,True,True,3)
        hb4.pack_start(self.btn_respond,False,False,3)
        hb4.show()
        vb.pack_start(hb4,True,True,3)

        lbl5 = gtk.Label(_("Respond1: "))
        lbl5.show()
        self.respond1 = gtk.Label()
        self.respond1.show()
        self.btn_respond1 = gtk.Button("...")
        self.btn_respond1.connect("clicked", self.on_sensor_select)
        self.btn_respond1.show()
        hb5 = gtk.HBox()
        hb5.pack_start(lbl5,False,False,3)
        hb5.pack_start(self.respond1,True,True,3)
        hb5.pack_start(self.btn_respond1,False,False,3)
        hb5.show()
        vb.pack_start(hb5,True,True,3)

        lbl6 = gtk.Label(_("Respond2: "))
        lbl6.show()
        self.respond2 = gtk.Label()
        self.respond2.show()
        self.btn_respond2 = gtk.Button("...")
        self.btn_respond2.connect("clicked", self.on_sensor_select)
        self.btn_respond2.show()
        hb6 = gtk.HBox()
        hb6.pack_start(lbl6,False,False,3)
        hb6.pack_start(self.respond2,True,True,3)
        hb6.pack_start(self.btn_respond2,False,False,3)
        hb6.show()
        vb.pack_start(hb6,True,True,3)

        vb.show()
        
        self.dlg_can = gtk.Dialog(_("Setup CAN node"),None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,(gtk.STOCK_OK,gtk.RESPONSE_OK,gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL)) 
        self.dlg_can.vbox.pack_start(vb,True,True,0)

        self.dlg_name = gtk.Dialog(_("Set name"),None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,(gtk.STOCK_OK,gtk.RESPONSE_OK,gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL)) 
        lb110 = gtk.Label(_("Name: "))
        lb110.show()
        self.netname = gtk.Entry()
        self.netname.set_width_chars(20)
        self.netname.set_max_length(80)
        self.netname.show()
        hb10 = gtk.HBox()
        hb10.pack_start(lb110,False,False,3)
        hb10.pack_start(self.netname,True,True,3)
        hb10.show()
        self.dlg_name.vbox.pack_start(hb10,True,True,0)

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
         
         iter = self.model.append(None,[name,"",None,"net",None,None])
         self.netlist.append([name,iter])
         self.add_node(cannode,node,iter)
         return True

    def add_node(self,cannode,node,iter):
         info  = 'nodeID=' + str(cannode.prop("nodeID"))
         info  = info + '; eds=' + str(cannode.prop("eds"))
         info  = info + ';...'
         return self.model.append(iter,[node.prop("name"),info,cannode,"node",iter,node])

    def on_button_press_event(self, object, event):                                                                                                                                 
#        print "*** on_button_press_event"
        (model, iter) = self.get_selection().get_selected()

        if event.button == 3:                                                                                                                                                       
            if not iter: return False
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
                     pass
                 elif t == "node":
                     self.on_edit_node_activate(None)
        return False

    def on_add_net_activate(self, menuitem):
        self.netname.set_text("")
        res = self.dlg_name.run()
        self.dlg_name.hide()
        if res != gtk.RESPONSE_OK:
            return

        name = self.netname.get_text()
        iter = self.model.append(None,[name,"",None,"net",None,None])
        self.netlist.append([name,iter])
        self.conf.mark_changes()

    def on_remove_net_activate(self, menuitem):
        self.conf.mark_changes()

    def check_node( self, node, rootiter ):
       it = self.model.iter_children(rootiter)
       while it is not None:                     
           if self.model.get_value(it,5) == node:
               return it
           it = self.model.iter_next(it)           
       
       return None     

    def check_nodeID( self, nodeID, rootiter ):
       it = self.model.iter_children(rootiter)
       while it is not None:                     
           if self.model.get_value(it,2).prop("nodeID") == nodeID:
               return it
           it = self.model.iter_next(it)           
       
       return None     

    def on_add_node_activate(self, menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return
        
        node = self.conf.dlg_nodes.run(self,None)
        if node == None:
             return
        
        etype = model.get_value(iter,3)
        
        rootiter=iter
        if etype == "node":
            rootiter = self.model.get_value(iter,4)
        
        if self.check_node(node,rootiter) != None:
           msg = "'" + node.prop("name") + "' " + _("already added!") 
           dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
           res = dlg.run()
           dlg.hide()
           return

        cnode = self.conf.xml.findMyLevel(node.children,"can")[0]
        if cnode == None:
            cnode = node.newChild(None,"can",None)
            if cnode == None:
               print "************** FAILED CREATE <can> for " + str(node.prop("name"))
               return        

        n = cnode.newChild(None,"item",None)
        n.setProp("net", self.model.get_value(rootiter,0))
        n.setProp("eds","")
        n.setProp("hbSensor","")
        n.setProp("nodeID","")
        n.setProp("respond","")
        n.setProp("respond1","")
        n.setProp("respond2","")
        it = self.add_node(n,node,rootiter)
        self.edit_node(it)
        self.conf.mark_changes()

    def on_remove_node_activate(self, menuitem):
        self.conf.mark_changes()

    def init_text_param(self,node,pname):
        t = node.prop(pname)
        if t == None:
            return ""
        return t

    def on_edit_node_activate(self, menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return
        self.edit_node(iter)

    def edit_node(self, iter): 
        cnode = self.model.get_value(iter,2) # can xmlnode
        node_xmlnode = self.model.get_value(iter,5) # node xmlnode

        self.eds.set_text( self.init_text_param(cnode,"eds") )
        self.node_id.set_text( self.init_text_param(cnode,"nodeID") )
        self.node_name.set_text( self.init_text_param(node_xmlnode,"name") )
        self.hb_sensor.set_text( self.init_text_param(cnode,"hbSensor") )
        self.respond.set_text( self.init_text_param(cnode,"respond") )
        self.respond1.set_text( self.init_text_param(cnode,"respond1") )
        self.respond2.set_text( self.init_text_param(cnode,"respond2") )
        
        res = self.dlg_can.run()
        self.dlg_can.hide()
        if res != gtk.RESPONSE_OK:
            return

        rootiter = self.model.get_value(iter,4) # NET level iterator
        nodeID = self.node_id.get_text()
        
        if nodeID != "":
             it1 = self.check_nodeID(nodeID,rootiter)
             if it1 != None and self.model.get_value(it1,2) != cnode:
                 msg = "'" + nodeID + "' " + _("already exist for %s") % self.model.get_value(it1,0)
                 dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
                 res = dlg.run()
                 dlg.hide()
                 return

        cnode.setProp("eds",self.eds.get_text())
        cnode.setProp("nodeID",nodeID)
        cnode.setProp("hbSensor",self.hb_sensor.get_text())
        cnode.setProp("respond",self.respond.get_text())
        cnode.setProp("respond1",self.respond1.get_text())
        cnode.setProp("respond2",self.respond2.get_text())

        info  = 'nodeID=' + str(cnode.prop("nodeID"))
        info  = info + '; eds=' + str(cnode.prop("eds"))
        info  = info + ';...'
        self.model.set_value(iter,1,info)
        self.conf.mark_changes()

    def on_sensor_action(self, lbl):
        self.conf.dlg_slist.set_selected_name(lbl.get_text())
        snode = self.conf.dlg_slist.run(self)
        if snode != None:
            lbl.set_text(snode.prop("name"))
  
    def on_sensor_select(self, btn):
        if btn == self.btn_sel_hbsensor:
            self.on_sensor_action(self.hb_sensor)
        if btn == self.btn_respond:
            self.on_sensor_action(self.respond)
        if btn == self.btn_respond1:
            self.on_sensor_action(self.respond1)
        if btn == self.btn_respond2:
            self.on_sensor_action(self.respond2)
         