# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_main
'''
Задачи:
1. Добавление, удаление карт ввода/вывода на узлах
2. Редактирование параметров каждого канала
'''
class IOMain(base_main.BaseMain):

    def __init__(self, conf):

        base_main.BaseMain.__init__(self,conf)
        conf.glade.signal_autoconnect(self)

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
            ["card_popup","io_card_popup",None,True], \
            ["node_popup","io_node_popup",None,True] \
        ]
        self.init_glade_elements(self.menu_list)

        self.build_tree()
        self.init_channels()

        # Список параметров для карты
        # ["class field","glade name","xmlname",save_xml_ignore_flag]
        self.card_params=[ \
            ["dlg_card","io_dlg_card","name",False], \
            ["card_num","io_sp_cardnum","card",False], \
            ["card_ba","io_baddr","baddr",False], \
            ["cb_cardlist","io_cb_cardlist","name",False] \
        ]
        self.init_glade_elements(self.card_params)        
        self.dlg_card.set_title(_("Select card"))
        
        # Список параметров для канала
        # ["class field","glade name","xmlname",save_xml_ignore_flag]
        self.channel_params=[ \
            # Common objects
            ["lbl_sensor","io_lbl_sensor","name",True], \
            ["dlg_param","io_dlg_channel",None,True], \
            ["parambook","ioparam_book",None,True], \
            ["dlg_info","io_lbl_info",None,True], \
            ["iotype","io_cbox_iotype","iotype",False], \
            # Common parameters
            ["tbl_comm","io_tbl_comm",None,True], \
            ["lamp","io_cb_lamp","lamp",False], \
            ["notestlamp","io_cb_notestlamp","notestlamp",False], \
            ["io_range","io_sp_range","range",False], \
            ["io_aref","io_sp_aref","aref",False], \
            ["safety","io_safety","safety",False], \
            ["breaklim","io_breaklim","breaklim",False], \
            ["defval","io_defval","default",False], \
            ["ioignore","io_cb_ignore","ioignore",False], \
            ["ioinvert","io_cb_invert","ioinvert",False], \
            # Calibrations
            ["calibr_param","io_tbl_calibration",None,True], \
            ["cdiagram","io_cbox_cdiagram","cdiagram",False], \
            ["cmin","io_cmin","cmin",False], \
            ["cmax","io_cmax","cmax",False], \
            ["rmin","io_rmin","rmin",False], \
            ["rmax","io_rmax","rmax",False], \
            ["prec","io_sp_precision","precision",False],
            ["noprec","io_cb_noprecision","noprecision",False], \
            # Delay`s
            ["ondelay","io_on_delay","ondelay",False], \
            ["offdelay","io_off_delay","offdelay",False], \
            ["jardelay","io_jar_delay","jardelay",False], \
            # Filters
            ["nofilter","io_cb_nofilter","nofilter",False], \
            ["median","io_sp_median","median",False], \
            ["leastsqr","io_sp_leastsqr","leatsqr",False], \
            ["filterIIR","io_sp_filterIIR","filterIIR",False], \
            ["filterRC","io_sp_filterRC","filterT",False], \
            ["average","io_sp_average","average",False], \
            # Thresholds
            ["tbl_tresholds","io_tbl_tresholds",None,True], \
            ["thr_hilimit","io_hilimit","hilimit",False], \
            ["thr_lowlimit","io_lowlimit","lowlimit",False], \
            ["thr_sensibility","io_sensibility","sensibility",False], \
            ["thr_inverse","io_cb_thr_invert","inverse",False], \
            ["thr_lbl_aID","io_lbl_aID","threshold_aid",False] \
           ]

        self.init_glade_elements(self.channel_params)

        self.sensor = None
        self.myedit_iter = None
        self.init_notebook_pages()
        self.build_cdiagram_list()
        self.dlg_param.set_title( _("Setup channel") )
        self.show_all()

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
        self.conf.s_dlg().set_selected_name(self.thr_lbl_aID.get_text())
        s = self.conf.s_dlg().run(self)
        if s != None:
            self.thr_lbl_aID.set_text(s.prop("name"))
            self.tbl_tresholds.set_sensitive(True)
        else:
            self.thr_lbl_aID.set_text("")
            self.tbl_tresholds.set_sensitive(False)
   
    def on_io_btn_sensor_clicked(self, button):
        self.conf.s_dlg().set_selected_name(self.lbl_sensor.get_text())
        while True:
            s = self.conf.s_dlg().run(self)
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
            break
 
        if self.sensor == None:
             self.tbl_comm.set_sensitive(False)
             self.set_combobox_element(self.iotype,"")
             self.lbl_sensor.set_text("")
        else:
             self.tbl_comm.set_sensitive(True)  
             self.set_combobox_element(self.iotype,self.sensor.prop("iotype"))
             self.lbl_sensor.set_text(self.sensor.prop("name"))

    def on_io_cbox_iotype_changed(self,combobox):
        # В зависимости от типа блокируем различные настройки
        t = combobox.get_active_text()
        if t == None:
             t = ""
        t = t.upper()
        if t == "DI" or t == "DO":
             self.pgCalibration.set_sensitive(False)
             self.lblcalibration.set_sensitive(False)
             self.pgFilter.set_sensitive(False)
             self.lblFilter.set_sensitive(False)
        else:
             self.pgCalibration.set_sensitive(True)
             self.lblcalibration.set_sensitive(True)
             self.pgFilter.set_sensitive(True)
             self.lblFilter.set_sensitive(True)
        
        if t == "AI" or t=="AO":
             self.pgThreshold.set_sensitive(False)
             self.lblThresholds.set_sensitive(False)
             self.pgDelay.set_sensitive(False)
             self.lblDelay.set_sensitive(False)
        else:
             self.pgThreshold.set_sensitive(True)
             self.lblThresholds.set_sensitive(True)
             self.pgDelay.set_sensitive(True)
             self.lblDelay.set_sensitive(True)
    
    def on_io_cbox_cdiagram_changed(self,combobox):
        if self.cdiagram.get_active_text() == "None":
            self.calibr_param.set_sensitive(True)
        else:
            self.calibr_param.set_sensitive(False)
    
    def set_sensitive_pages(self):
         if self.sensor == None:
             self.pgCalibration.set_sensitive(False)
             self.lblcalibration.set_sensitive(False)
             self.pgFilter.set_sensitive(False)
             self.lblFilter.set_sensitive(False)
             self.pgThreshold.set_sensitive(False)
             self.lblThresholds.set_sensitive(False)
             self.pgDelay.set_sensitive(False)
             self.lblDelay.set_sensitive(False)
             self.tbl_comm.set_sensitive(False)
         else:
             self.on_io_cbox_iotype_changed(self.iotype)
             self.tbl_comm.set_sensitive(True)
    
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
           print "WARNING: add empty card name.. "
           return

        node = model.get_value(node_iter,2)
        cnode = self.conf.xml.findMyLevel(node.children,"iocards")[0]
        
        if cnode == None:
           cnode = node.newChild(None,"iocards",None)
           if cnode == None:
               print "************** FAILED CREATE <iocards> for " + str(node)
               return
 
        n = cnode.newChild(None,"item",None)
        self.save2xml_elements_value(self.card_params,n)
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
        self.init_elements_value(self.card_params,cnode)
        # при редактировании отключаем выбор, т.к.
        # сменить тип карты можно только удалив старую
        # (со всеми привязками и т.п)
        self.cb_cardlist.set_sensitive(False)
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

        self.save2xml_elements_value(self.card_params,cnode)
        model.set_value(iter,4,cnum)
        info  = 'card=' + str(cnode.prop("card"))
        info  = info + ' BA=' + str(cnode.prop("baddr"))
        model.set_value(iter,1,info)
        self.conf.mark_changes()

    def on_edit_channel(self,iter):
        card_iter = self.model.iter_parent(iter)
        card = self.model.get_value(card_iter,2)
        node_iter = self.model.iter_parent(card_iter)
        node = self.model.get_value(node_iter,2)
        node_id = self.model.get_value(node_iter,4) # node.prop("id")

        self.sensor = self.model.get_value(iter,2)
        snode = UniXML.EmptyNode()
        if self.sensor != None:
            snode = self.sensor  
        self.set_sensitive_pages()
        self.init_elements_value(self.channel_params,snode)
        
        if self.thr_lbl_aID.get_text() == "":
            self.tbl_tresholds.set_sensitive(False)
        else:
            self.tbl_tresholds.set_sensitive(True)
        
        prev_sensor = self.sensor
        txt = _("Setup ") + str(card.prop("name")) + ":" + str(self.model.get_value(iter,0))
        self.dlg_info.set_text(txt)
        self.myedit_iter = iter
        
        while True:
            res = self.dlg_param.run()
            self.dlg_param.hide()
            if res != gtk.RESPONSE_OK:
                return
            
            if self.sensor == None: # "очищаем старую привязку"
                if prev_sensor != None:
                     self.save2xml_elements_value(self.channel_params,prev_sensor,"")
                self.model.set_value(iter,2,None)
                self.model.set_value(iter,1,"")
                self.myedit_iter = None
                self.conf.mark_changes()
                return

            cres,badparam = self.validate_elements(self.channel_params)
            if cres == False:
                 msg = _("Incorrect value: '") + str(badparam) + "'"
                 dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
                 res = dlg.run()
                 dlg.hide()
                 continue
            break
        
        if self.sensor == None: # "очищаем старую привязку"
            self.save2xml_elements_value(self.channel_params,prev_sensor,"")
            self.model.set_value(iter,2,None)
            self.model.set_value(iter,1,"")
            self.myedit_iter = None
            self.conf.mark_changes()
            return

        self.myedit_iter = None
        
        # Сохраняем параметры
        self.model.set_value(iter,2,self.sensor)
        self.model.set_value(iter,1,self.sensor.prop("name"))
        self.sensor.setProp("io",node_id)
        self.sensor.setProp("card",card.prop("card"))
        self.sensor.setProp("subdev", str(self.model.get_value(iter,5)))
        self.sensor.setProp("channel",str(self.model.get_value(iter,4)))
        # Остальные параметры по списку
        self.save2xml_elements_value(self.channel_params,self.sensor)
        self.conf.mark_changes()
