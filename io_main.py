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
        conf.glade.signal_autoconnect(self)

        gtk.TreeView.__init__(self)
        self.model = None
        self.modelfilter = None
        #                          Name | Parameters | xmlnode | element type | number | subdev
        self.model = gtk.TreeStore(gobject.TYPE_STRING,gobject.TYPE_STRING,object,gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING)
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

        self.dlg_card = conf.glade.get_widget("io_dlg_card")
        self.dlg_card.set_title(_("Select card"))
        self.card_num = conf.glade.get_widget("io_sp_cardnum")
        self.card_ba = conf.glade.get_widget("io_baddr")
        self.cb_cardlist = conf.glade.get_widget("io_cb_cardlist")

        # Parameters dialog
        self.dlg_param = conf.glade.get_widget("dlg_ioparam")
        self.dlg_param.set_title( _("Setup channel") )
        self.parambook = conf.glade.get_widget("ioparam_book")
        self.init_notebook_pages()
        
        self.lbl_sensor = conf.glade.get_widget("io_lbl_sensor")
        self.sensor = None
        self.myedit_iter = None
        self.dlg_info = conf.glade.get_widget("io_lbl_info")
        self.iotype = conf.glade.get_widget("io_cbox_iotype")
        
        # Common parameters
        self.lamp = conf.glade.get_widget("io_cb_lamp")
        self.notestlamp = conf.glade.get_widget("io_cb_notestlamp")
        self.io_range = conf.glade.get_widget("io_sp_range")
        self.io_aref = conf.glade.get_widget("io_sp_aref")
        self.safety = conf.glade.get_widget("io_safety")
        self.breaklim = conf.glade.get_widget("io_breaklim")
        self.defval = conf.glade.get_widget("io_defval")
        self.ignore = conf.glade.get_widget("io_cb_ignore")
        self.invert = conf.glade.get_widget("io_cb_invert")
        
        # Calibrations
        self.calibr_param = conf.glade.get_widget("io_tbl_calibration")
        self.cdiagram = conf.glade.get_widget("io_cbox_cdiagram")
        self.build_cdiagram_list()
        self.cmin = conf.glade.get_widget("io_cmin")
        self.cmax = conf.glade.get_widget("io_cmax")
        self.rmin = conf.glade.get_widget("io_rmin")
        self.rmax = conf.glade.get_widget("io_rmax")
        self.prec = conf.glade.get_widget("io_sp_precision")
        self.noprec = conf.glade.get_widget("io_cb_noprecision")

        # Delay`s
        self.ondelay = conf.glade.get_widget("io_on_delay")
        self.offdelay = conf.glade.get_widget("io_off_delay")
        self.jardelay = conf.glade.get_widget("io_jar_delay")
        
        # Filters
        self.nofilter = conf.glade.get_widget("io_cb_nofilter")
        self.median = conf.glade.get_widget("io_sp_median")
        self.leastsqr = conf.glade.get_widget("io_sp_leastsqr")
        self.filterIIR = conf.glade.get_widget("io_sp_filterIIR")
        self.filterRC = conf.glade.get_widget("io_sp_filterRC")
        self.average = conf.glade.get_widget("io_sp_average")
 
        print "*************** nofilter: " + str(self.nofilter.__class__.__name__)
        print "*************** average: " + str(self.average.__class__.__name__)
        print "*************** offdelay: " + str(self.offdelay.__class__.__name__)
        
        
        self.init_glade_elements([["io_sp_median","median"],["io_sp_average","average"]])
        
        self.show_all()

    def init_glade_elements(self, elist):
        # Инициализация переменных из glade файла... по списку
        # состоящему из элементов вида ["gladename","var name"]
        print "********* init list: count: " + str(len(elist))
        for e in elist:
            self.__dict__[e[0]] = e[1]
            
    def set_prop(self):
        return self.prop


    def init_notebook_pages(self):
        # читаем все страницы и создаём нужные нам поля класса
        # (для управления доступностью закладок)
        # не очень конечно выгляди, но работает..
        nums = self.parambook.get_n_pages()
        for n in range(0,nums):
            p = self.parambook.get_nth_page(n)
            if p == None:
              continue
            lbl =  self.parambook.get_tab_label(p)
            if lbl == None:
              continue
            if lbl.get_name() == "io_pgComm":
               self.pgComm = p
               self.lblComm = lbl
            elif lbl.get_name() == "io_pgCalibration":
               self.pgCalibration = p
               self.lblcalibration = lbl
            elif lbl.get_name() == "io_pgDelay":
               self.pgDelay = p
               self.lblDelay = lbl
            elif lbl.get_name() == "io_pgFilter":
               self.pgFilter = p
               self.lblFilter = lbl
            elif lbl.get_name() == "io_pgThreshold":
               self.pgThreshold = p
               self.lblThresholds = lbl

    def build_cdiagram_list(self):
        lstore = gtk.ListStore(gobject.TYPE_STRING)
        lstore.clear()
        cell = gtk.CellRendererText()
        self.cdiagram.pack_start(cell, True)
        self.cdiagram.add_attribute(cell, 'text', 0)
        self.cdiagram.set_model(lstore)
        lstore.append(["None"])
        n = self.conf.xml.findNode(self.conf.xml.getDoc(),"Calibrations")[0]
        if n == None:
            return
        node = self.conf.xml.firstNode(n.children.next)
        while node != None:
            dname = str(node.prop("name"))
            lstore.append([dname])
            node = self.conf.xml.nextNode(node)

    def build_tree(self):
        node = self.conf.xml.findNode(self.conf.xml.getDoc(),"nodes")[0].children.next 
#        iter0 = self.model.append(None, [_("Nodes"),"",None,"",-1,-1,None])
        while node != None:
            info = "id=" + str(node.prop("id")) + " ip=" + node.prop("ip")
            iter1 = self.model.append(None,[node.prop("name"),info,node,"node",node.prop("id"),0])
            self.read_cards(node,iter1)
            node = self.conf.xml.nextNode(node)

    def read_cards(self,rootnode,iter):
        rnode = self.conf.xml.findMyLevel(rootnode.children,"iocards")[0] # .children.next
        if rnode == None: return
        node = rnode.children.next
        
        while node != None:
            info  = 'card=' + str(node.prop("card"))
            info  = info + ' BA=' + str(node.prop("baddr"))
            iter2 = self.model.append(iter, [node.prop("name"),info,node,"card",node.prop("card"),0])
            self.build_channels_list(node,self.model,iter2)
            node = self.conf.xml.nextNode(node)

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
            model.append(iter, [_("ch_")+str(i),"",None,"channel",str(i),"0"])

    def build_ai16_list(self,card,model,iter):
        for i in range(0,8):
            model.append(iter, [_("J2:")+str(i),"",None,"channel",str(i),"0"])
        for i in range(0,8):
            model.append(iter, [_("J3:")+str(i),"",None,"channel",str(i),"1"])

    def build_unio48_list(self,card,model,iter):
        for i in range(0,24):
            model.append(iter, [_("J1:")+str(i),"",None,"channel",str(i),"0"])
        for i in range(0,24):
            model.append(iter, [_("J2:")+str(i),"",None,"channel",str(i),"1"])

    def build_unio96_list(self,card,model,iter):
        for i in range(0,24):
            model.append(iter, [_("J1:")+str(i),"",None,"channel",str(i),"0"])
        for i in range(0,24):
            model.append(iter, [_("J2:")+str(i),"",None,"channel",str(i),"1"])
        for i in range(0,24):
            model.append(iter, [_("J3:")+str(i),"",None,"channel",str(i),"2"])
        for i in range(0,24):
            model.append(iter, [_("J4:")+str(i),"",None,"channel",str(i),"3"])

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
    
    def check_connection(self,snode, myiter):
       it = self.model.get_iter_first() # node level
       myname = self.model.get_value(myiter,0)
       while it is not None: 
           it_card = self.model.iter_children(it) # card level
           if it_card is not None:
                while it_card != None:
                    it_ch = self.model.iter_children(it_card) # channel level
                    if it_ch != None:
                         while it_ch != None:
                             if self.model.get_value(it_ch,2) == snode:
                                   # пропускаем себя..
                                   if self.model.get_value(it_ch,0) != myname:
                                       return [it,it_card,it_ch]
                             it_ch = self.model.iter_next(it_ch)
                    it_card = self.model.iter_next(it_card)
           it = self.model.iter_next(it)           
       
       return [None,None,None]

    def on_button_press_event(self, object, event):                                                                                                                                 
#        print "*** on_button_press_event"
        (model, iter) = self.get_selection().get_selected()

        if event.button == 3:                                                                                                                                                       
            if not iter: return False
            t = model.get_value(iter,3)
            if t == "card":
                self.card_popup.popup(None, None, None, event.button, event.time)                                                                                                       
                return False                                                                                                                                                         
            if t == "node":
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
                 if t == "node":
                     pass
                 elif t == "card": 
                     self.on_edit_card_activate(None)
                 elif t == "channel":
                     self.on_edit_channel(iter)

        return False

    def on_dlg_card_btnCancel_clicked(self, button):
       self.dlg_card.response(gtk.RESPONSE_CANCEL)

    def on_dlg_card_btnOK_clicked(self,button):
       self.dlg_card.response(gtk.RESPONSE_OK)

    def on_io_btnCancel_clicked(self, button):
       self.dlg_param.response(gtk.RESPONSE_CANCEL)

    def on_io_btnOK_clicked(self,button):
       self.dlg_param.response(gtk.RESPONSE_OK)

    def on_io_btn_aID_clicked(self,button):
        pass

    def set_iotype(self,iotype):
        model = self.iotype.get_model()
        it = model.get_iter_first()
        while it is not None:                     
            if iotype.upper() == str(model.get_value(it,0)).upper():
                 self.iotype.set_active_iter(it)
                 return
            it = model.iter_next(it)
    
    def set_cdiagram(self,name):
        if name == None:
            return
        model = self.cdiagram.get_model()
        it = model.get_iter_first()
        while it is not None:                     
            if name.upper() == str(model.get_value(it,0)).upper():
                 self.iotype.set_active_iter(it)
                 return
            it = model.iter_next(it)

    def on_io_btn_sensor_clicked(self, button):
        self.conf.dlg_slist.set_selected_name(self.lbl_sensor.get_text())
        
        while True:
            s = self.conf.dlg_slist.run(self)
            if s != None:
                n_it,cd_it,ch_it = self.check_connection(s,self.myedit_iter)
                if ch_it is not None:
                    msg = "'" + s.prop("name") + "' " + _("Already connection!") 
                    addr = " (" + self.model.get_value(n_it,0) + ":" + self.model.get_value(cd_it,0) + ":" + self.model.get_value(ch_it,0) +_(")\n Reconnection?")
                    msg = msg + addr
                    dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,msg)
                    res = dlg.run()
                    dlg.hide()
                    if res == gtk.RESPONSE_NO:
                        return False
                    # сперва очистим привязку у старого
                    self.model.set_value(ch_it,2,None)
                    self.model.set_value(ch_it,1,"")
            self.sensor = s  
            self.lbl_sensor.set_text(self.sensor.prop("name"))
            self.set_iotype(self.sensor.prop("iotype"))
            break

    def on_io_cbox_iotype_changed(self,combobox):
        # В зависимости от типа блокируем различные настройкистроим
        pass
    
    def on_io_cbox_cdiagram_changed(self,combobox):
        if self.cdiagram.get_active_text() == "None":
            self.calibr_param.set_sensitive(True)
        else:
            self.calibr_param.set_sensitive(False)
    
    def on_add_card_activate(self,menuitem):
    
        (model, iter) = self.get_selection().get_selected()
        if not iter: return

        t = model.get_value(iter,3)
        node_iter = None
        if t == "card":
            node_iter = self.model.iter_parent(iter)
        elif t == "node":
            node_iter = iter
        else:
            print "*** FAILED ELEMENT TYPE " + t
            return

        while True:
            res = self.dlg_card.run()
            self.dlg_card.hide()
            if res != gtk.RESPONSE_OK:  
                return
            # check card number
            cnum = self.card_num.get_value_as_int()
            it1 = self.check_cardnum(cnum,node_iter,iter)
            if it1 != None:
               msg = "card number='" + str(cnum) + "' " + _("already exist for %s") % self.model.get_value(it1,0)
               dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
               res = dlg.run()
               dlg.hide()
               continue
            # check baddr
            s_baddr = self.card_ba.get_text()
            baddr = 0
            if s_baddr != "":
                 baddr = int(eval(s_baddr))
            it1 = self.check_baddr(baddr,node_iter,iter)
            if baddr!=0 and it1 != None:
               msg = "base address='" + s_baddr + "' " + _("already exist for %s") % self.model.get_value(it1,0)
               dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
               res = dlg.run()
               dlg.hide()
               continue

            break                

        cname = self.cb_cardlist.get_active_text()
        if cname == "":
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

        it = self.model.append(node_iter, [n.prop("name"),info,n,"card",n.prop("card"),0])
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
        
        cnode = self.model.get_value(iter,2)
        node_iter = self.model.iter_parent(iter)
        pnode = self.model.get_value(node_iter,2)

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

    def check_cardnum(self,num, iter, selfiter):
        it = self.model.iter_children(iter)
        myname = self.model.get_value(selfiter,0)
        while it is not None:
            if self.model.get_value(it,0) == myname:
                it = self.model.iter_next(it)  
                continue
            s_n = self.model.get_value(it,2).prop("card")
            n = 0
            if s_n != None and s_n!="":
                n = int(s_n)

            if n == num:
                return it
            it = self.model.iter_next(it)
       
        return None 	  

    def check_baddr(self,baddr, iter, selfiter):
        it = self.model.iter_children(iter)
        myname = self.model.get_value(selfiter,0)
        while it is not None:
            if self.model.get_value(it,0) == myname:
                it = self.model.iter_next(it)  
                continue
            s_n = self.model.get_value(it,2).prop("baddr")
            n = 0
            if s_n != "":
                n = int(eval(s_n))

            if n == baddr:
                return it
            it = self.model.iter_next(it)           
    
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
        
        while True:
            res = self.dlg_card.run()
            self.dlg_card.hide()
            self.cb_cardlist.set_sensitive(True)
            if res != gtk.RESPONSE_OK:
                return
            
            # check card number
            cnum = self.card_num.get_value_as_int()
            it1 = self.check_cardnum(cnum,self.model.iter_parent(iter),iter)
            if it1 != None:
               msg = "card number='" + str(cnum) + "' " + _("already exist for %s") % self.model.get_value(it1,0)
               dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
               res = dlg.run()
               dlg.hide()
               continue
            # check baddr
            s_baddr = self.card_ba.get_text()
            baddr = 0
            if s_baddr != "":
                 baddr = int(eval(s_baddr))
            it1 = self.check_baddr(baddr,self.model.iter_parent(iter),iter)
            if baddr!=0 and it1 != None:
               msg = "base address='" + s_baddr + "' " + _("already exist for %s") % self.model.get_value(it1,0)
               dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
               res = dlg.run()
               dlg.hide()
               continue

            break                

        cnode.setProp("card",str(cnum))
        cnode.setProp("baddr",str(baddr))
        model.set_value(iter,4,cnum)

        info  = 'card=' + str(cnode.prop("card"))
        info  = info + ' BA=' + str(cnode.prop("baddr"))
        model.set_value(iter,1,info)
        self.conf.mark_changes()


    def check_calibrations_params(self):
       # для начала проверим на "цифру"
       if self.cmin.get_text()!="" and self.conf.check_value_int(self.cmin.get_text()) == False:
          return [False,"cmin"]
       if self.cmax.get_text()!="" and self.conf.check_value_int(self.cmax.get_text()) == False:
          return [False,"cmax"]
       if self.rmin.get_text()!="" and self.conf.check_value_int(self.rmin.get_text()) == False:
           return [False,"rmin"]
       if self.rmax.get_text()!="" and self.conf.check_value_int(self.rmax.get_text()) == False:
          return [False,"rmax"]

       return [True,""]

    def check_delay_params(self):
       # для начала проверим на "цифру"
       if self.ondelay.get_text()!="" and self.conf.check_value_int(self.ondelay.get_text()) == False:
          return [False, _("on delay")]
       if self.offdelay.get_text()!="" and self.conf.check_value_int(self.offdelay.get_text()) == False:
          return [False,_("off delay")]
       if self.jardelay.get_text()!="" and self.conf.check_value_int(self.jardelay.get_text()) == False:
           return [False, _("jar delay")]

       return [True,""]
       
    def check_comm_params(self):
       if self.safety.get_text()!="" and self.conf.check_value_int(self.safety.get_text()) == False:
          return [False, _("safety")]
       if self.defval.get_text()!="" and self.conf.check_value_int(self.defval.get_text()) == False:
          return [False, _("default")]
       if self.breaklim.get_text()!="" and self.conf.check_value_int(self.breaklim.get_text()) == False:
          return [False, _("breaklim")]
     
       return [True,""]

    def set_xml_param(self,xmlnode,proplist=[],val=""):
        if xmlnode == None:
             return

        for p in proplist:
            xmlnode.setProp(p,val)
    
    def get_int_val(self,str_val):
        if str_val == "" or str_val == None: 
            return 0

        return int(str_val)

    def get_str_val(self,str_val):
        if str_val == None: 
            return ""

        return str_val

    def init_dlg_parameters(self,iter):
        self.sensor = self.model.get_value(iter,2)
        
        snode = UniXML.EmptyNode()
        if self.sensor != None:
            snode = self.sensor  
            self.set_iotype(self.sensor.prop("iotype"))

        self.lbl_sensor.set_text(self.get_str_val(snode.prop("name")))

        # Common parameters
        self.lamp.set_active( self.get_int_val(snode.prop("lamp")) )
        self.notestlamp.set_active(self.get_int_val(snode.prop("notestlamp")))
        self.io_range.set_value( self.get_int_val(snode.prop("range")) )
        self.io_aref.set_value( self.get_int_val(snode.prop("aref")) )
        self.safety.set_text( self.get_str_val(snode.prop("safety")) )
        self.breaklim.set_text( self.get_str_val(snode.prop("breaklim")) )
        self.defval.set_text( self.get_str_val(snode.prop("default")) )
        self.ignore.set_active( self.get_int_val(snode.prop("ignore")) )
        self.invert.set_active( self.get_int_val(snode.prop("invert")) )
        
        # Calibrations
        self.cmin.set_text( self.get_str_val(snode.prop("cmin")) )
        self.cmax.set_text( self.get_str_val(snode.prop("cmax")) )
        self.rmin.set_text( self.get_str_val(snode.prop("rmin")) )
        self.rmax.set_text( self.get_str_val(snode.prop("rmax")) )
        self.prec.set_value( self.get_int_val(snode.prop("precision")) )
        self.noprec.set_active( self.get_int_val(snode.prop("noprecision")) )
        self.set_cdiagram(snode.prop("caldiagram"))

        # Filter
#        self.nofilter.set_active( self.get_int_val(snode.prop("nofilter")) )
#        self.median.set_value( self.get_int_val(snode.prop("filtermedian")) )
#        self.leastsqr.set_value( self.get_int_val(snode.prop("leatsqr")) )
#        self.filterIIR.set_value( self.get_int_val(snode.prop("iir_thr")) )
#        self.filterRC.set_value( self.get_int_val(snode.prop("filterT")) )
#        self.average.set_value( self.get_int_val(snode.prop("average")) )

        # Delays
        self.jardelay.set_text( self.get_str_val(snode.prop("jardelay")) )
        self.ondelay.set_text( self.get_str_val(snode.prop("ondelay")) )
        self.offdelay.set_text( self.get_str_val(snode.prop("offdelay")) )
        
        # Thresolds
         
        
    def get_cb_param(self, checkbutton):
        if checkbutton.get_active():
            return "1"
        return ""
    
    
    def on_edit_channel(self,iter):

        card_iter = self.model.iter_parent(iter)
        card = self.model.get_value(card_iter,2)
        node_iter = self.model.iter_parent(card_iter)
        node = self.model.get_value(node_iter,2)
        node_id = self.model.get_value(node_iter,4) # node.prop("id")
        prev_sensor = self.model.get_value(iter,2)
        self.init_dlg_parameters(iter)
        
        txt = _("Setup ") + str(card.prop("name")) + ":" + str(self.model.get_value(iter,0))
        self.dlg_info.set_text(txt)
        self.myedit_iter = iter
        
        while True:
            res = self.dlg_param.run()
            self.dlg_param.hide()
            if res != gtk.RESPONSE_OK:
                return

            if self.sensor == None: # "очищаем старую привязку"
                self.set_xml_param(prev_sensor,["lamp","notestlamp","range","aref","safety",\
                       "breaklim","default","ignore","invert","cmin","cmax","rmin","rmax",\
                       "precision","noprecision"],"")
                self.model.set_value(iter,2,None)
                self.model.set_value(iter,1,"")
                return
            # Common parameters
#     проверку перенёс в
#            if self.sensor != None:
#                n_it,cd_it,ch_it = self.check_connection(self.sensor,iter)
#                if ch_it is not None:
#                    msg = "'" + self.sensor.prop("name") + "' " + _("Already connection!") 
#                    addr = " (" + self.model.get_value(n_it,0) + ":" + self.model.get_value(cd_it,0) + ":" + self.model.get_value(ch_it,0) +_(")\n Reconnection?")
#                    msg = msg + addr
#                    dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,msg)
#                    res = dlg.run()
#                    dlg.hide()
#                    if res == gtk.RESPONSE_NO:
#                         return False
#                    # сперва очистим привязку у старого
#                    self.model.set_value(ch_it,2,None)
#                    self.model.set_value(ch_it,1,"")

            cres,badparam = self.check_comm_params() 
            if cres == False:
                 msg = _("Incorrect value of common parameter: '") + str(badparam) + "'"
                 dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
                 res = dlg.run()
                 dlg.hide()
                 continue

            # Calibrations
            cres,badparam = self.check_calibrations_params() 
            if cres == False:
                 msg = _("Incorrect value of calibrations: '") + str(badparam) + "'"
                 dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
                 res = dlg.run()
                 dlg.hide()
                 continue
            # Delay`s
            cres,badparam = self.check_delay_params() 
            if cres == False:
                 msg = _("Incorrect value of delay`s: '") + str(badparam) + "'"
                 dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
                 res = dlg.run()
                 dlg.hide()
                 continue        
            
            # Filter
            # Threshold
            
            break
        
        self.myedit_iter = None
        
        # Сохраняем параметры
        self.model.set_value(iter,2,self.sensor)
        self.model.set_value(iter,1,self.sensor.prop("name"))

        self.sensor.setProp("io",node_id)
        self.sensor.setProp("card",card.prop("card"))
        self.sensor.setProp("subdev", str(self.model.get_value(iter,5)))
        self.sensor.setProp("channel",str(self.model.get_value(iter,4)))
        
        # Common parameters
        self.sensor.setProp("lamp", self.get_cb_param(self.lamp) )
        self.sensor.setProp("notestlamp", self.get_cb_param(self.notestlamp) )
        self.sensor.setProp("range", str(self.io_range.get_value_as_int()))
        self.sensor.setProp("aref", str(self.io_aref.get_value_as_int()))
        self.sensor.setProp("safety", str(self.safety.get_text()))
        self.sensor.setProp("breaklim", str(self.breaklim.get_text()))
        self.sensor.setProp("default", str(self.defval.get_text()))
        self.sensor.setProp("ioignore", self.get_cb_param(self.ignore) )
        self.sensor.setProp("ioinvert", self.get_cb_param(self.invert) )
        
        # Calibrations
        self.sensor.setProp("cmin", self.cmin.get_text())
        self.sensor.setProp("cmax", self.cmax.get_text())
        self.sensor.setProp("rmin", self.rmin.get_text())
        self.sensor.setProp("rmax", self.rmax.get_text())
        self.sensor.setProp("precision", str(self.prec.get_value_as_int()))
        self.sensor.setProp("noprecision", self.get_cb_param(self.noprec) )
        
        # Filter
        self.sensor.setProp("nofilter", self.get_cb_param(self.noprec) )
        
        # Delays
        self.sensor.setProp("jardelay", self.jardelay.get_text())
        self.sensor.setProp("ondelay", self.ondelay.get_text())
        self.sensor.setProp("offdelay", self.offdelay.get_text())
        
        # Threshold
        
        
        self.conf.mark_changes()
