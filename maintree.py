# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import iocards

TARGET_STRING = 0
TARGET_ROOTWIN = 1

target = [
    ('STRING', 0, TARGET_STRING),
    ('text/plain', 0, TARGET_STRING),
    ('application/x-rootwin-drop', 0, TARGET_ROOTWIN)
]

class MainTree(gtk.TreeView):

    xml = None

    def __init__(self, conf):

        self.conf = conf

        gtk.TreeView.__init__(self)
        self.model = None
        self.modelfilter = None
        self.model = gtk.TreeStore(gobject.TYPE_STRING,gobject.TYPE_STRING,object)
        self.modelfilter = self.model.filter_new()

        # create treeview
        self.set_model(self.model)
        self.set_rules_hint(True)
        self.connect("button-press-event", self.on_button_press_event)

        self.add_columns()

        # expand all rows after the treeview widget has been realized
#       self.connect('realize', lambda tv: tv.expand_all())

        self.build_tree()

        self.show_all()

    def build_tree(self):

        node = self.conf.xml.findNode(self.conf.xml.getDoc(),"nodes")[0].children.next 
        iter0 = self.model.append(None, [_("Nodes"),"",None])
        while node != None:
            iter1 = self.model.append(iter0,[node.prop("name"),"",node])
            self.read_cards(node,iter1)
            node = self.conf.xml.nextNode(node)

    def read_cards(self,rootnode,iter):

        c = iocards.IOCards()
        rnode = self.conf.xml.findNode(rootnode,"iocards")[0] # .children.next
        if rnode == None:
        	return
        
        node = rnode.children.next
        
        while node != None:
            info  = 'card=' + str(node.prop("card"))
            iter2 = self.model.append(iter, [node.prop("name"),info,node])
            c.build_channels_list(node,self.model,iter2)
            self.init_channels(node,iter2)
            node = self.conf.xml.nextNode(node)

    def init_channels(self,cardnode,rootiter):
#        card = cardnode.prop("card")
#        self.model.set_value(rootiter,1,"4**test information")
         pass
        
    def add_columns(self):
        
        renderer = gtk.CellRendererText()
        renderer.set_property("xalign", 0.0)
        column = gtk.TreeViewColumn(_("Name"), renderer, text=0)
        column.set_clickable(False)
        self.append_column(column)

        renderer = gtk.CellRendererText()
        renderer.set_property("xalign", 0.0)
        column = gtk.TreeViewColumn(_("Information"), renderer, text=1)
        column.set_clickable(False)
        self.append_column(column)

    def on_button_press_event(self, object, event):                                                                                                                                 
#        print "*** on_button_press_event"

#        if event.button == 3:                                                                                                                                                       
#            self.popup_menu.popup(None, None, None, event.button, event.time)                                                                                                       
#            return True                                                                                                                                                         
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:                                                                                                              
            (model, iter) = self.get_selection().get_selected()                                                                                                                         
            if not iter:                                                                                                                                                                
                 return True
            else :
#                c = card.Card( model.get_value(iter, 2) )
#                self.model.clear()
#                self.iotree.read_channels(c)
                 pass
	    return True
