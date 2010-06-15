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

        gtk.TreeView.__init__(self)
        self.model = None
        self.modelfilter = None
        #                          Name | Parameters | xmlnode | element type | parent iterator | node_xmlnode
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

        lb10 = gtk.Label(_("          Node: "))
        lb10.show()
        self.node_name = gtk.Label()
        self.node_name.show()
        hb0 = gtk.HBox()
        self.btn_selnode = gtk.Button("...")
        self.btn_selnode.connect("clicked", self.on_node_select)
        self.btn_selnode.show()
        hb0.pack_start(lb10,False,False,3)
        hb0.pack_start(self.node_name,True,True,3)
        hb0.pack_start(self.btn_selnode,False,False,3)
        hb0.show()
        vb.pack_start(hb0,True,True,3)

        lb1 = gtk.Label(_("CAN NodeID: "))
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

        lb11 = gtk.Label(_("      eds file: "))
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

        lbl2 = gtk.Label(_("      hbSensor: "))
        lbl2.show()
        self.hb_sensor = gtk.Label()
        self.hb_sensor.show()
        self.btn_sel_hbsensor = gtk.Button("...")
        self.btn_sel_hbsensor.connect("clicked", self.on_node_select)
        self.btn_sel_hbsensor.show()
        hb3 = gtk.HBox()
        hb3.pack_start(lbl2,False,False,3)
        hb3.pack_start(self.hb_sensor,True,True,3)
        hb3.pack_start(self.btn_sel_hbsensor,False,False,3)
        hb3.show()
        vb.pack_start(hb3,True,True,3)

        vb.show()
        
        self.dlg_can = gtk.Dialog(_("Setup CAN node"),None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,(gtk.STOCK_OK,gtk.RESPONSE_OK,gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL)) 
        self.dlg_can.vbox.pack_start(vb,True,True,0)

        self.show_all()

    def build_tree(self):
        node = self.conf.xml.findNode(self.conf.xml.getDoc(),"CAN_Net")[0].children.next 
        while node != None:
            iter1 = self.model.append(None,[node.prop("name"),node.prop("comment"),node,"net",None,None])
            self.read_nodes(node,iter1)
            node = self.conf.xml.nextNode(node)

    def read_nodes(self,rootnode,iter):
        node = self.conf.xml.getNode(rootnode.children)
        while node != None:
            info  = ' eds=' + str(node.prop("eds"))
            info  = info + ' nodeID=' + str(node.prop("nodeID"))
            info  = info + '...'
            iter2 = self.model.append(iter, [node.prop("name"),info,node,"node",iter,self.find_node(node.prop("name"))])
            node = self.conf.xml.nextNode(node)

    def find_node(self, node_name):
        node = self.conf.xml.findNode(self.conf.xml.getDoc(),"nodes")[0].children.next 
        while node != None:
            if node.prop("name") == node_name:
                return node
            node = self.conf.xml.nextNode(node)           
        return None
    
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
        self.conf.mark_changes()
        pass

    def on_remove_net_activate(self, menuitem):
        self.conf.mark_changes()
        pass

    def on_add_node_activate(self, menuitem):
        self.conf.mark_changes()
        pass

    def on_remove_node_activate(self, menuitem):
        self.conf.mark_changes()
        pass

    def init_text_param(self,node,pname):
        t = node.prop(pname)
        if t == None:
            return ""
        return t

    def on_edit_node_activate(self, menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return

        cnode = model.get_value(iter,2) # can xmlnode
        node_xmlnode = model.get_value(iter,5) # node xmlnode

        self.eds.set_text( self.init_text_param(cnode,"eds") )
        self.node_id.set_text( self.init_text_param(cnode,"nodeID") )
        self.node_name.set_text( self.init_text_param(cnode,"name") )
        self.hb_sensor.set_text( self.init_text_param(cnode,"hbSensor") )
        
        res = self.dlg_can.run()
        self.dlg_can.hide()
        if res != gtk.RESPONSE_OK:
            return

#        cnode.setProp("card",str(self.card_num.get_value_as_int()))
#        cnode.setProp("baddr",self.card_ba.get_text())

#        info  = 'card=' + str(cnode.prop("card"))
#        info  = info + ' BA=' + str(cnode.prop("baddr"))
#        model.set_value(iter,1,info)
        self.conf.mark_changes()

    def on_node_select(self, btn):
        if btn == self.btn_selnode:
             print "****** node select"
             node = self.conf.dlg_nodes.run(self,"") # self.node_name.get_text())
             if node != None:
                 self.node_name.set_text(node.prop("name"))
        elif btn == self.btn_sel_hbsensor:
             print "****** hb sensor select " + self.hb_sensor.get_text()
             snode = self.conf.dlg_slist.run(self,"") # self.hb_sensor.get_text())
             if snode != None:
                 self.hb_sensor.set_text(snode.prop("name"))
         