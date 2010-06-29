# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_main
'''
Редактирование списка узлов
'''
class NodesMain(base_main.BaseMain):

    def __init__(self, conf):

        base_main.BaseMain.__init__(self,conf)
        conf.glade.signal_autoconnect(self)

        self.model = None
        self.modelfilter = None
        #                          Name | Parameters | xmlnode
        self.model = gtk.TreeStore(gobject.TYPE_STRING,gobject.TYPE_STRING,object)
        self.modelfilter = self.model.filter_new()

#        self.modelfilter.set_visible_column(1)

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

        self.menu_list = [ \
            ["node_popup","nodes_popup",None,True] \
        ]
        self.init_glade_elements(self.menu_list)

        self.build_tree()
     
    def build_tree(self):
        node = self.conf.xml.findNode(self.conf.xml.getDoc(),"nodes")[0].children.next 
        while node != None:
            info = "id=" + str(node.prop("id")) + " ip=" + node.prop("ip")
            iter1 = self.model.append(None,[node.prop("name"),info,node])
            node = self.conf.xml.nextNode(node)

    def on_button_press_event(self, object, event):                                                                                                                                 
#        print "*** on_button_press_event"
        (model, iter) = self.get_selection().get_selected()

        if event.button == 3:                                                                                                                                                       
            if not iter: return False
            self.node_popup.popup(None, None, None, event.button, event.time)
            return False
        
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            if not iter:                                                                                                                                                                
                 return False
        return False

#    def on_dlg_card_btnCancel_clicked(self, button):
#       self.dlg_card.response(gtk.RESPONSE_CANCEL)

#    def on_dlg_card_btnOK_clicked(self,button):
#       self.dlg_card.response(gtk.RESPONSE_OK)
    
    def on_remove_node_activate(self,menuitem):
        print "On remove activate.."
        pass
    
    def on_add_node_activate(self,menuitem):
        print "On add activate.."
        pass
    
    def on_edit_node_activate(self,menuitem):
        print "On edit activate.."
        pass
