# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure

class IOMain(gtk.TreeView):

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

        self.card_popup = gtk.Menu() 
        i0 = gtk.MenuItem( _("add new card") ) 
        i0.connect("activate", self.on_add_card_activate)
        i0.show() 
        self.card_popup.append(i0) 

        i1 = gtk.MenuItem( _("remove card") ) 
        i1.connect("activate", self.on_remove_card_activate)
        i1.show() 
        self.card_popup.append(i1) 

        i2 = gtk.MenuItem( _("edit") ) 
        i2.connect("activate", self.on_edit_card_activate)
        i2.show() 
        self.card_popup.append(i2) 

        self.node_popup = gtk.Menu() 
        i0 = gtk.MenuItem( _("add new card") ) 
        i0.connect("activate", self.on_add_card_activate)
        i0.show() 
        self.node_popup.append(i0) 

        self.build_tree()
        self.init_channels()

        self.cb_cardlist = gtk.combo_box_new_text()
        for cname in self.get_card_list():
            self.cb_cardlist.append_text(cname)

        self.cb_cardlist.show_all()

        self.dlg_card = gtk.Dialog(_("Select card"),None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,(gtk.STOCK_OK,gtk.RESPONSE_OK,gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
        
        vb = gtk.VBox()
        
        hb = gtk.HBox()

        lb = gtk.Label(_(" Card number: "))
        lb.show()
        self.card_num = gtk.SpinButton()
        self.card_num.set_range(0,10)
        self.card_num.set_increments(1,1)
        self.card_num.set_digits(0)
        self.card_num.show()

        hb.pack_start(lb,False,False,3)
        hb.pack_start(self.card_num,True,True,3)
        hb.show()

        lb1 = gtk.Label(_("Base address: "))
        lb1.show()
        self.card_ba = gtk.Entry()
        self.card_ba.set_width_chars(5)
        self.card_ba.set_max_length(8)
        self.card_ba.show()
        hb1 = gtk.HBox()
        hb1.pack_start(lb1,False,False,3)
        hb1.pack_start(self.card_ba,True,True,3)
        hb1.show()

        vb.pack_start(self.cb_cardlist,True,True,3)
        vb.pack_start(hb,True,True,3)
        vb.pack_start(hb1,True,True,3)
        vb.show()
        self.dlg_card.vbox.pack_start(vb,True,True,0)

        self.show_all()

    def build_tree(self):
        node = self.conf.xml.findNode(self.conf.xml.getDoc(),"nodes")[0].children.next 
#        iter0 = self.model.append(None, [_("Nodes"),"",None,"",-1,-1,None])
        while node != None:
            info = "id=" + str(node.prop("id")) + " ip=" + node.prop("ip")
            iter1 = self.model.append(None,[node.prop("name"),info,node,"n",node.prop("id"),0,None])
            self.read_cards(node,iter1)
            node = self.conf.xml.nextNode(node)

    def read_cards(self,rootnode,iter):
        rnode = self.conf.xml.findMyLevel(rootnode.children,"iocards")[0] # .children.next
        if rnode == None: return
        node = rnode.children.next
        
        while node != None:
            info  = 'card=' + str(node.prop("card"))
            info  = info + ' BA=' + str(node.prop("baddr"))
            iter2 = self.model.append(iter, [node.prop("name"),info,node,"s",node.prop("card"),0,iter])
            self.build_channels_list(node,self.model,iter2)
            node = self.conf.xml.nextNode(node)

    def get_card_list(self):
        return ["DI32","AI16","UNIO48","UNIO96"]
 
    def build_channels_list(self,cardnode,model,iter):
        if cardnode.prop("name") == "DI32":
            self.build_di32_list(cardnode,model,iter)
        elif cardnode.prop("name") == "AI16":
            self.build_ai16_list(cardnode,model,iter)
        elif cardnode.prop("name") == "UNIO48":
            self.build_unio48_list(cardnode,model,iter)
        elif cardnode.prop("name") == "UNIO96":
            self.build_unio96_list(cardnode,model,iter)
    
    def build_di32_list(self,card,model,iter):
        for i in range(0,32):
            model.append(iter, [_("ch_")+str(i),"",card,"c",str(i),"0",iter])

    def build_ai16_list(self,card,model,iter):
        for i in range(0,8):
            model.append(iter, [_("J2:")+str(i),"",card,"c",str(i),"0",iter])
        for i in range(0,8):
            model.append(iter, [_("J3:")+str(i),"",card,"c",str(i),"1",iter])

    def build_unio48_list(self,card,model,iter):
        for i in range(0,24):
            model.append(iter, [_("J1:")+str(i),"",card,"c",str(i),"0",iter])
        for i in range(0,24):
            model.append(iter, [_("J2:")+str(i),"",card,"c",str(i),"1",iter])

    def build_unio96_list(self,card,model,iter):
        for i in range(0,24):
            model.append(iter, [_("J1:")+str(i),"",card,"c",str(i),"0",iter])
        for i in range(0,24):
            model.append(iter, [_("J2:")+str(i),"",card,"c",str(i),"1",iter])
        for i in range(0,24):
            model.append(iter, [_("J3:")+str(i),"",card,"c",str(i),"2",iter])
        for i in range(0,24):
            model.append(iter, [_("J4:")+str(i),"",card,"c",str(i),"3",iter])

    def init_channels(self):
    # проходим по <sensors> и если поля заполнены ищем в нашем TreeView
        node = self.conf.xml.findNode(self.conf.xml.getDoc(),"sensors")[0].children.next 
        while node != None:
            if node.prop("io") != None:
                  self.find_node(node)
            node = self.conf.xml.nextNode(node)    

    def find_node(self,node):
        it = self.model.get_iter_first()
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

    def check_connection(self,snode,it0):
       it = self.model.iter_children(it0)
       while it is not None:                                                                                                                                                        
           if self.model.get_value(it,2) == snode:
               return [snode,it]
           
           s,i = self.check_connection(snode,it)
           if s is not None: return [s,i]
           
           it = self.model.iter_next(it)           
       
       return [None,None]                                                                                              

    def on_button_press_event(self, object, event):                                                                                                                                 
#        print "*** on_button_press_event"
        (model, iter) = self.get_selection().get_selected()

        if event.button == 3:                                                                                                                                                       
            if not iter: return False
            t = model.get_value(iter,3)
            if t == "s":
                self.card_popup.popup(None, None, None, event.button, event.time)                                                                                                       
                return False                                                                                                                                                         
            if t == "n":
                self.node_popup.popup(None, None, None, event.button, event.time)                                                                                                       
                return False

#        if event.button == 1 and event.type != gtk.gdk._2BUTTON_PRESS:
#            self.expand_row( model.get_path(iter), False )
#            return False

        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            if not iter:                                                                                                                                                                
                 return False
            else :
                 t = model.get_value(iter,3)
#            	 print "********* select: " + str(t)
                 if t == "n": # node elemnt
                     pass
                 elif t == "s": # card element
                     self.on_edit_card_activate(None)
                 elif t == "c": # channel element
                     snode = self.conf.dlg_slist.run(self,model.get_value(iter,2))
                     if snode != None:

                         card_iter = model.get_value(iter,6)
                         card = model.get_value(card_iter,2)
                         
                         node_iter = model.get_value(card_iter,6)
                         node = model.get_value(node_iter,2)
                         node_id = model.get_value(node_iter,4) # node.prop("id")
#                         if node_id == "": node_id = node.prop("name")
                     
                         it0 = self.model.get_iter_first()
                         cn,it = self.check_connection(snode,it0)
                         if cn is not None:
#                             print "************** ALREADY EXIST: " + str(cn)
                             msg = "'" + snode.prop("name") + "' " + ("Already connection!") 
                             addr = " (" + node.prop("name") + ":" + self.model.get_value(card_iter,0) + ":" + model.get_value(it,4) +")\n Reconnection?"
                             msg = msg + addr
                             dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,msg)
                             res = dlg.run()
                             dlg.hide()
                             if res == gtk.RESPONSE_NO:
                                 return False
                             # сперва очистим привязку у старого
                             model.set_value(it,2,None)
                             model.set_value(it,1,"")
                             cn.setProp("io","")
                             cn.setProp("card","")
                             cn.setProp("subdev", "")
                             cn.setProp("channel","")
                             
                         
                         model.set_value(iter,2,snode)
                         model.set_value(iter,1,snode.prop("name"))

                         snode.setProp("io",node_id);
                         snode.setProp("card",card.prop("card"));
                         snode.setProp("subdev", str(model.get_value(iter,5)));
                         snode.setProp("channel",str(model.get_value(iter,4)));
                         self.conf.mark_changes()

        return False

    def on_add_card_activate(self,menuitem):
    
        (model, iter) = self.get_selection().get_selected()
        if not iter: return

        res = self.dlg_card.run()
        self.dlg_card.hide()
        if res != gtk.RESPONSE_OK:  
            return
 
        cname = self.cb_cardlist.get_active_text()
        if cname == "":
           return

        t = model.get_value(iter,3)
        node_iter = None
        if t == "s":
            node_iter = model.get_value(iter,6)
        elif t == "n":
            node_iter = iter
        else:
            print "*** FAILED ELEMENT TYPE " + t
            return

        node = model.get_value(node_iter,2)

        cnode = self.conf.xml.findMyLevel(node.children,"iocards")[0]

        if cnode == None:
           cnode = node.newChild(None,"iocards",None)
           if cnode == None:
               print "************** FAILED CREATE <iocards> for " + str(node)
               return

        n = cnode.newChild(None,"item",None)
        n.setProp("name",cname)
        n.setProp("card",str(self.card_num.get_value_as_int()))
        n.setProp("baddr",self.card_ba.get_text())
        self.conf.mark_changes()

        info  = 'card=' + str(n.prop("card"))
        info  = info + ' BA=' + str(n.prop("baddr"))

        it = self.model.append(node_iter, [n.prop("name"),info,n,"s",n.prop("card"),0,node_iter])
        self.build_channels_list(n,self.model,it)
        self.conf.mark_changes()

    def on_remove_card_activate(self,menuitem):

        (model, iter) = self.get_selection().get_selected()
        if not iter: return

        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,_("You are sure?"))
        res = dlg.run()
        dlg.hide()
        if res == gtk.RESPONSE_NO:
            return False
        
        cnode = model.get_value(iter,2)
        node_iter = model.get_value(iter,6)
        pnode = model.get_value(node_iter,2)

        cn = cnode.prop("card")
        nn = pnode.prop("id")

        node = self.conf.xml.findNode(self.conf.xml.getDoc(),"sensors")[0].children.next 
        while node != None:
            if node.prop("io") == nn and node.prop("card") == cn:
                  node.unsetProp("io")
                  node.unsetProp("card")
                  node.unsetProp("subdev")
                  node.unsetProp("channel")

            node = self.conf.xml.nextNode(node)
    
        cnode.unlinkNode()    
        model.remove(iter)
        self.conf.mark_changes()

    def on_edit_card_activate(self,menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return

        cnode = model.get_value(iter,2)

        self.cb_cardlist.set_sensitive(False)

		# select card
        cn = cnode.prop("name")
        m = self.cb_cardlist.get_model()
        it = m.get_iter_first()
        while it != None:
           if str(m.get_value(it,0)) == cn:
                self.cb_cardlist.set_active_iter(it)
                break
           it = m.iter_next(it)           

        ba = cnode.prop("baddr")
        if ba == None:
            ba = ""
        self.card_num.set_value( int(cnode.prop("card")))
        self.card_ba.set_text(ba)
        res = self.dlg_card.run()
        self.dlg_card.hide()
        self.cb_cardlist.set_sensitive(True)
        if res != gtk.RESPONSE_OK:
            return

        cnode.setProp("card",str(self.card_num.get_value_as_int()))
        cnode.setProp("baddr",self.card_ba.get_text())

        info  = 'card=' + str(cnode.prop("card"))
        info  = info + ' BA=' + str(cnode.prop("baddr"))
        model.set_value(iter,1,info)
        self.conf.mark_changes()
