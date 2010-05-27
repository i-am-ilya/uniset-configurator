# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure

class MainTree(gtk.TreeView):

    xml = None

    def __init__(self, conf):

        self.conf = conf

        gtk.TreeView.__init__(self)
        self.model = None
        self.modelfilter = None
        #                          Name | Parameters | xmlnode | element type | number | subdev | parent iterator
        self.model = gtk.TreeStore(gobject.TYPE_STRING,gobject.TYPE_STRING,object,gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,object)
        self.modelfilter = self.model.filter_new()

#        self.modelfilter.set_visible_column(1)

        # create treeview
        self.set_model(self.model)
        self.set_rules_hint(True)
        self.connect("button-press-event", self.on_button_press_event)

        self.add_columns()

        # expand all rows after the treeview widget has been realized
#       self.connect('realize', lambda tv: tv.expand_all())

        self.build_tree()
        self.init_channels()

        self.show_all()

    def build_tree(self):
        node = self.conf.xml.findNode(self.conf.xml.getDoc(),"nodes")[0].children.next 
        iter0 = self.model.append(None, [_("Nodes"),"",None,"",-1,-1,None])
        while node != None:
            iter1 = self.model.append(iter0,[node.prop("name"),"",node,"n",node.prop("id"),0,iter0])
            self.read_cards(node,iter1)
            node = self.conf.xml.nextNode(node)

    def read_cards(self,rootnode,iter):
        rnode = self.conf.xml.findNode(rootnode,"iocards")[0] # .children.next
        if rnode == None: return
        node = rnode.children.next
        
        while node != None:
            info  = 'card=' + str(node.prop("card"))
            iter2 = self.model.append(iter, [node.prop("name"),info,node,"s",node.prop("card"),0,iter])
            self.build_channels_list(node,self.model,iter2)
            node = self.conf.xml.nextNode(node)
 
    def build_channels_list(self,cardnode,model,iter):
        if cardnode.prop("name") == "DI32":
            self.build_di32_list(cardnode,model,iter)
        elif cardnode.prop("name") == "AI16":
            self.build_ai16_list(cardnode,model,iter)
    
    def build_di32_list(self,card,model,iter):
        for i in range(0,32):
            model.append(iter, [_("ch_")+str(i),"",card,"c",str(i),"0",iter])

    def build_ai16_list(self,card,model,iter):
        for i in range(0,8):
            model.append(iter, [_("J2:")+str(i),"",card,"c",str(i),"0",iter])
        for i in range(0,8):
            model.append(iter, [_("J3:")+str(i),"",card,"c",str(i),"1",iter])

    def init_channels(self):
    # проходим по <sensors> и если поля заполнены ищем в нашем TreeView
        node = self.conf.xml.findNode(self.conf.xml.getDoc(),"sensors")[0].children.next 
        while node != None:
            if node.prop("io") != None:
                  self.find_node(node)
            node = self.conf.xml.nextNode(node)    

    def find_node(self,node):
       it = self.model.iter_children(self.model.get_iter_first())
       node_id = node.prop("io")
       while it is not None:
           if self.model.get_value(it,4) == node_id:
               it1 = self.model.iter_children(it)
               self.find_card(it1,node)
               return
           
           it = self.model.iter_next(it)

    def find_card(self,it,node):
       card_num = node.prop("card")
       while it is not None:
           if self.model.get_value(it,4) == card_num:
               it2 = self.model.iter_children(it)
               self.find_subdev(it2,node)
               return

           it = self.model.iter_next(it)

    def find_subdev(self,it,node):
       sb = node.prop("subdev")
       while it is not None:
           if self.model.get_value(it,5) == sb:
               self.find_channel(it,node)
               return

           it = self.model.iter_next(it)

    def find_channel(self,it,node):
       ch = node.prop("channel")
       while it is not None:
           if self.model.get_value(it,4) == ch:
               self.model.set_value(it,2,node)
               self.model.set_value(it,1,node.prop("name"))
               return

           it = self.model.iter_next(it)
        
    def add_columns(self):
        
        renderer = gtk.CellRendererText()
#        renderer.set_property("xalign", 0.0)
        column = gtk.TreeViewColumn(_("Name"), renderer, text=0)
        column.set_clickable(False)
        self.append_column(column)

        renderer = gtk.CellRendererText()
#        renderer.set_property("xalign", 0.0)
        column = gtk.TreeViewColumn(_("Parameters"), renderer, text=1)
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
                 t = model.get_value(iter,3)
#            	 print "********* select: " + str(t)
                 if t == "n": # node elemnt
                     pass
                 elif t == "s": # card element
                     pass
                 elif t == "c": # channel element
                     snode = self.conf.dlg_slist.run(self,model.get_value(iter,2))
                     if snode != None:
                         model.set_value(iter,2,snode)
                         model.set_value(iter,1,snode.prop("name"))
                         
                         card_iter = model.get_value(iter,6)
                         card = model.get_value(card_iter,2)
                         
                         node_iter = model.get_value(card_iter,6)
                         node = model.get_value(node_iter,2)

                         node_id = model.get_value(node_iter,4) # node.prop("id")
#                         if node_id == "": node_id = node.prop("name")

                         snode.setProp("io",node_id);
                         snode.setProp("card",card.prop("card"));
                         snode.setProp("subdev", str(model.get_value(iter,5)));
                         snode.setProp("channel",str(model.get_value(iter,4)));
                         self.conf.mark_changes()
	
	    return True
