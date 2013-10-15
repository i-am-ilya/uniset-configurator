# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import re
import datetime
import UniXML
import configure
import base_editor
import uniset_io_conf
import card_editor
from global_conf import *

class fid():
  name = 0
  param = 1
  xmlnode = 2
  etype = 3
  num = 4
  subdev = 5
  pic = 6
  comm = 7
  
pic_CARD = 'card.png'
pic_NODE = 'node.png'  
pic_CHAN = 'channel.png' 
'''
Задачи:
1. Добавление, удаление карт ввода/вывода на узлах
2. Редактирование параметров каждого канала
'''
class IOEditor(base_editor.BaseEditor,gtk.Viewport):

    def __init__(self, conf):

        base_editor.BaseEditor.__init__(self,conf)
        gtk.Viewport.__init__(self)

        self.ioconf = uniset_io_conf.IOConfig(conf.xml,conf.datdir)
        self.editor = card_editor.CardEditor(conf,self.ioconf,conf.datdir)

        self.glade = gtk.glade.XML(conf.datdir+"uniset-io.glade")
        self.glade.signal_autoconnect(self)

        vbox = self.glade.get_widget("mainbox")
        vbox.reparent(self)

        box = self.glade.get_widget("tree_win")
        self.tv = gtk.TreeView()
        self.tv.show_all()
        box.add(self.tv)

        self.fentry = self.glade.get_widget("io_filter_entry")
        self.filter_cb_case = self.glade.get_widget("io_filter_cb_case")
        

        self.model = None
        self.modelfilter = None
        self.model = gtk.TreeStore(gobject.TYPE_STRING, # name
                                   gobject.TYPE_STRING, # Parameters
                                   object,              # xmlnode
                                   gobject.TYPE_STRING, # element type
                                   gobject.TYPE_STRING, # number
                                   gobject.TYPE_STRING, # subdev
                                   gtk.gdk.Pixbuf,      # picture
                                   gobject.TYPE_STRING) # comment)
        
        self.fmodel = self.model.filter_new()
        self.fmodel.set_visible_func(self.view_filter_func)
        self.tv.set_model(self.fmodel)
        self.tv.set_rules_hint(True)
        self.tv.connect("button-press-event", self.on_button_press_event)
        
        column = gtk.TreeViewColumn(_("Name"))
        nmcell = gtk.CellRendererText()
        pbcell = gtk.CellRendererPixbuf()
        column.pack_start(pbcell, False)
        column.pack_start(nmcell, False)
        column.set_attributes(pbcell,pixbuf=fid.pic)
        column.set_attributes(nmcell,text=fid.name)
        column.set_clickable(False)
        self.tv.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Parameters"), renderer, text=fid.param)
        column.set_clickable(False)
        self.tv.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("subdev"), renderer, text=fid.subdev)
        column.set_clickable(False)
        self.tv.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("comment"), renderer, text=fid.comm)
        column.set_clickable(False)
        self.tv.append_column(column)

        # expand all rows after the treeview widget has been realized
#       self.connect('realize', lambda tv: tv.expand_all())

        self.menu_list = [
            ["card_popup","io_card_popup",None,True],
            ["node_popup","io_node_popup",None,True],
            ["channel_popup","io_channel_popup",None,True],
            ["mi_channel_edit","io_mi_channel_edit",None,True],
            ["mi_channel_add","io_mi_channel_add",None,True],
            ["mi_channel_remove","io_mi_channel_remove",None,True]
        ]
        self.init_glade_elements(self.menu_list,self.glade)

        # Список параметров для канала
        # ["class field","glade name","xmlname",save_xml_ignore_flag]
        self.channel_params=[
            # Common objects
            ["lbl_sensor","io_lbl_sensor","name",True],
            ["dlg_param","io_dlg_channel",None,True],
            ["parambook","ioparam_book",None,True],
            ["dlg_info","io_lbl_info",None,True],
            ["iotype","io_cbox_iotype","iotype",False,True],
            # Common parameters
            ["tbl_comm","io_tbl_comm",None,True],
            ["lamp","io_cb_lamp","lamp",False],
            ["notestlamp","io_cb_notestlamp","no_iotestlamp",False],
            ["io_range","io_sp_range","range",False],
            ["io_aref","io_sp_aref","aref",False],
            ["safety","io_safety","safety",False],
            ["breaklim","io_breaklim","breaklim",False],
            ["defval","io_defval","default",False],
            ["ioignore","io_cb_ignore","ioignore",False],
            ["ioinvert","io_cb_invert","ioinvert",False],
            # Calibrations
            ["calibr_param","io_tbl_calibration",None,True],
            ["cdiagram","io_cbox_cdiagram","cdiagram",False],
            ["cmin","io_cmin","cmin",False],
            ["cmax","io_cmax","cmax",False],
            ["rmin","io_rmin","rmin",False],
            ["rmax","io_rmax","rmax",False],
            ["prec","io_sp_precision","precision",False],
            ["noprec","io_cb_noprecision","noprecision",False],
            # Delay`s
            ["ondelay","io_on_delay","ondelay",False],
            ["offdelay","io_off_delay","offdelay",False],
            ["jardelay","io_jar_delay","jardelay",False],
            # Filters
            ["nofilter","io_cb_nofilter","nofilter",False],
            ["median","io_sp_median","median",False],
            ["leastsqr","io_sp_leastsqr","leatsqr",False],
            ["filterIIR","io_sp_filterIIR","filterIIR",False],
            ["filterRC","io_sp_filterRC","filterT",False],
            ["average","io_sp_average","average",False],
            # Thresholds
            ["tbl_tresholds","io_tbl_tresholds",None,True],
            ["thr_hilimit","io_hilimit","hilimit",False],
            ["thr_lowlimit","io_lowlimit","lowlimit",False],
            ["thr_sensibility","io_sensibility","sensibility",False],
            ["thr_inverse","io_cb_thr_invert","inverse",False],
            ["thr_lbl_aID","io_lbl_aID","threshold_aid",False]
        ]

        self.init_glade_elements(self.channel_params,self.glade)

        self.io_params=[
            ["","","channel",False],
            ["","","card",False],
            ["","","subdev",False],
            ["","","io",False]
        ]

        self.sensor = None
        self.myedit_iter = None
        self.init_notebook_pages()
        self.dlg_param.set_title( _("Setup channel") )
        
        self.reopen()
        self.show_all()

    def init_editor(self):
        base_editor.BaseEditor.init_editor(self)

        # подключение к редактору узлов (для отслеживания изменений в списке узлов)
        n_editor = self.conf.n_editor()
        if n_editor != None:
            n_editor.connect("change-node",self.nodeslist_change)
            n_editor.connect("add-new-node",self.nodeslist_add)
            n_editor.connect("remove-node",self.nodeslist_remove)

    def reopen(self):
        self.model.clear()
        self.build_tree()
        self.init_channels()
        self.build_cdiagram_list()
    
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
        img = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_NODE)
        while node != None:
            info = self.get_node_info(node)
            #img = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_NODE)
            iter1 = self.model.append(None,[node.prop("name"),info,node,"node",node.prop("name"),"",img,node.prop("comment")])
            self.read_cards(node,iter1)
            node = self.conf.xml.nextNode(node)

    def read_cards(self,rootnode,iter):
        rnode = self.conf.xml.findMyLevel(rootnode.children,"iocards")[0] # .children.next
        if rnode == None: return
        node = rnode.children.next
        img = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_CARD)
        while node != None:
            info = self.get_card_info(node)
            iter2 = self.model.append(iter, [node.prop("name").upper(),info,node,"card",node.prop("card"),"",img,node.prop("comment")])
            self.build_channels_list(node,self.model,iter2)
            node = self.conf.xml.nextNode(node)

    def get_card_info(self,xmlnode):
        info  = 'card=' + str(xmlnode.prop("card"))
        info  = info + ' BA=' + str(xmlnode.prop("baddr"))
        return info
    
    def build_channels_list(self,cardnode,model,iter):
        img = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_CHAN)
        clst = self.ioconf.get_channel_list(cardnode)
        for c in clst:
            model.append(iter, [c[1],"",None,"channel",str(c[0]),str(c[3]),img,""])

        #self.ioconf.build_channels_list(cardnode,model,iter,img)

    def init_channels(self):
        # проходим по <sensors> и если поля заполнены ищем в нашем TreeView
        node = self.conf.xml.findNode(self.conf.xml.getDoc(),"sensors")[0].children.next 
        while node != None:
            if node.prop("io") != None and node.prop("threshold_aid") == None:
                 self.find_node(node)
            node = self.conf.xml.nextNode(node)    

    def find_node(self,node):
        it = self.model.get_iter_first()
        node_id = node.prop("io")
        while it is not None:
           if self.model.get_value(it,fid.num) == node_id:
               it1 = self.model.iter_children(it)
               self.find_card(it1,node)
               return
           
           it = self.model.iter_next(it)

    def find_card(self,it,node):
        card_num = node.prop("card")
        while it is not None:
            if self.model.get_value(it,fid.num) == card_num:
                it2 = self.model.iter_children(it)
                self.find_subdev(it2,node)
                return

            it = self.model.iter_next(it)

    def find_subdev(self,it,node):
        sb = node.prop("subdev")
        while it is not None:
            if self.model.get_value(it,fid.subdev) == sb:
                self.find_channel(it,node)
                return

            it = self.model.iter_next(it)

    def find_channel(self,it,node):
       ch = node.prop("channel")
       while it is not None:
           if self.model.get_value(it,fid.num) == ch:
               self.model.set_value(it,fid.xmlnode,node)
               self.model.set_value(it,fid.param,self.get_sensor_info(node))
               return

           it = self.model.iter_next(it)
        
    def check_connection(self,snode, myiter):
       it = self.model.get_iter_first() # node level
       myname = self.model.get_value(myiter,fid.name)
       while it is not None: 
           it_card = self.model.iter_children(it) # card level
           if it_card is not None:
                while it_card != None:
                    it_ch = self.model.iter_children(it_card) # channel level
                    if it_ch != None:
                         while it_ch != None:
                             if self.model.get_value(it_ch,fid.xmlnode) == snode:
                                   # пропускаем себя..
                                   if self.model.get_value(it_ch,fid.name) != myname:
                                       return [it,it_card,it_ch]
                             it_ch = self.model.iter_next(it_ch)
                    it_card = self.model.iter_next(it_card)
           it = self.model.iter_next(it)           
       
       return [None,None,None]

    def on_button_press_event(self, object, event):                                                                                                                                 
#        print "*** on_button_press_event"
        (model, iter) = self.tv.get_selection().get_selected()

        if event.button == 3:                                                                                                                                                       
            if not iter: return False
            t = model.get_value(iter,fid.etype)
            if t == "card":
                self.card_popup.popup(None, None, None, event.button, event.time)                                                                                                       
                return False                                                                                                                                                         
            if t == "node":
                self.node_popup.popup(None, None, None, event.button, event.time)                                                                                                       
                return False
            if t == "channel":
                con = model.get_value(iter,fid.xmlnode)
                if con != None:
                   self.mi_channel_remove.set_sensitive(True)
                   self.mi_channel_edit.set_sensitive(True)
                   self.mi_channel_add.set_sensitive(False)
                else:
                   self.mi_channel_remove.set_sensitive(False)
                   self.mi_channel_edit.set_sensitive(False)
                   self.mi_channel_add.set_sensitive(True)
                   
                self.channel_popup.popup(None, None, None, event.button, event.time)                                                                                                       
                return False

#        if event.button == 1 and event.type != gtk.gdk._2BUTTON_PRESS:
#            self.expand_row( model.get_path(iter), False )
#            return False

        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            if not iter:                                                                                                                                                                
                 return False
            else :
                 t = model.get_value(iter,fid.etype)
#            	 print "********* select: " + str(t)
                 if t == "node":
                     pass
                 elif t == "card": 
                     self.on_edit_card_activate(None)
                 elif t == "channel":
                     self.on_edit_channel(iter)

        return False
 
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
                iotype = s.prop("iotype")
                p_iter = self.model.iter_parent(self.myedit_iter)
                cardname = self.model.get_value(p_iter,fid.name)
                chan = self.model.get_value(self.myedit_iter,fid.num)
                subdev = self.model.get_value(self.myedit_iter,fid.subdev)
                c_iotype = self.ioconf.get_iotype(cardname,subdev,chan)
           
                if c_iotype != "" and iotype != c_iotype:
                    msg = "'" + s.prop("name") + "' " + _("Difference in the types: card channel iotype '%s' != you selected '%s'.\n")%(c_iotype,iotype)
                    msg = msg + " Change the type of sensor?"
                    dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,msg)
                    # dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
                    res = dlg.run()
                    dlg.hide()
                    if res == gtk.RESPONSE_NO:        
                       return False
                    s.setProp("iotype",c_iotype)

                n_it,cd_it,ch_it = self.check_connection(s,self.myedit_iter)
                if ch_it is not None:
                    msg = "'" + s.prop("name") + "' " + _("Already connection!") 
                    addr = " (" + self.model.get_value(n_it,fid.name) + ":" + self.model.get_value(cd_it,fid.name) + ":" + self.model.get_value(ch_it,fid.name) +_(")\n Reconnection?")
                    msg = msg + addr
                    dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,msg)
                    res = dlg.run()
                    dlg.hide()
                    if res == gtk.RESPONSE_NO:
                        return False

                    # сперва очистим привязку у старого
                    self.model.set_value(ch_it,fid.xmlnode,None)
                    self.model.set_value(ch_it,fid.param,"")
                
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
             iotype = self.sensor.prop("iotype")
             if iotype == "DI" or iotype == "AI":
                self.iotype.set_sensitive(False)
                self.lamp.set_sensitive(False)
             else:
                self.iotype.set_sensitive(True)
                self.lamp.set_sensitive(True)
        
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
             
        if t == "DI" or t == "AI":
           self.lamp.set_sensitive(False)
        else:
           self.lamp.set_sensitive(True)
    
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
    
    def on_io_channel_edit_activate(self,menuitem):
        (model, iter) = self.tv.get_selection().get_selected()
        if not iter: return	  
        self.on_edit_channel(iter)	  
    
    def on_io_channel_add_activate(self,menuitem):
        (model, iter) = self.tv.get_selection().get_selected()
        if not iter: return	  
        self.on_edit_channel(iter)
    
    def on_io_channel_remove_activate(self,menuitem):
        (model, iter) = self.tv.get_selection().get_selected()
        if not iter: return
        
        t = model.get_value(iter,fid.etype)
        if t != "channel": 
           return
        
        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,_("Are you sure?"))
        res = dlg.run()
        dlg.hide()
        if res == gtk.RESPONSE_NO:
            return False        
        
        xmlnode = model.get_value(iter,fid.xmlnode)
        if xmlnode == None: 
           return
        
        self.save2xml_elements_value(self.io_params,xmlnode,"")

        i_iter = self.fmodel.convert_iter_to_child_iter(iter)
        self.model.set_value(i_iter,fid.xmlnode,None)
        self.model.set_value(i_iter,fid.param,"")
        self.conf.mark_changes()
                
    def on_add_card_activate(self,menuitem):
    
        (model, iter) = self.tv.get_selection().get_selected()
        if not iter: return

        t = model.get_value(iter,fid.etype)
        node_iter = None
        if t == "card":
            node_iter = self.model.iter_parent(iter)
        elif t == "node":
            node_iter = iter
        else:
            print "*** FAILED ELEMENT TYPE " + t
            return

        while True:
            res = self.editor.run()
            if res != dlg_RESPONSE_OK:  
                return
            # check card number
            cnum = self.editor.card_num()
            it1 = self.check_cardnum(cnum,node_iter,iter,model)
            if it1 != None:
               msg = "card number='" + str(cnum) + "' " + _("already exist for %s") % model.get_value(it1,fid.name)
               dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
               res = dlg.run()
               dlg.hide()
               continue
            # check baddr
            s_baddr = self.editor.ba()
            baddr = 0
            if s_baddr != "":
                 try:
                     baddr = int(eval(s_baddr))
                 except NameError:
                    msg = _("Wrong 'Base address' value")
                    dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
                    res = dlg.run()
                    dlg.hide()
                    continue
            
            it1 = self.check_baddr(baddr,node_iter,iter,model)
            if baddr!=0 and it1 != None:
               msg = "base address='" + s_baddr + "' " + _("already exist for %s") % model.get_value(it1,fid.name)
               dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
               res = dlg.run()
               dlg.hide()
               continue

            break                

        cname = self.editor.card_name()
        if cname == "":
           print "WARNING: add empty card name.. "
           return

        node = model.get_value(node_iter,fid.xmlnode)
        cnode = self.conf.xml.findMyLevel(node.children,"iocards")[0]
        
        if cnode == None:
           cnode = node.newChild(None,"iocards",None)
           if cnode == None:
               print "************** FAILED CREATE <iocards> for " + str(node)
               return
 
        n = cnode.newChild(None,"item",None)
        self.editor.save(n)
        self.conf.mark_changes()
        img = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_CARD)

        i_node_iter = self.fmodel.convert_iter_to_child_iter(node_iter)
        it = self.model.append(i_node_iter, [n.prop("name"),self.get_card_info(n),n,"card",n.prop("card"),"0",img,n.prop("comment")])
        self.build_channels_list(n,self.model,it)
        self.conf.mark_changes()

    def on_remove_card_activate(self,menuitem):

        (model, iter) = self.tv.get_selection().get_selected()
        if not iter: return

        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,_("Are you sure?"))
        res = dlg.run()
        dlg.hide()
        if res == gtk.RESPONSE_NO:
            return False
        
        cnode = model.get_value(iter,fid.xmlnode)
        node_iter = model.iter_parent(iter)
        pnode = model.get_value(node_iter,fid.xmlnode)

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

        self.editor.delete(cnode)
        cnode.unlinkNode()

        i_iter = self.fmodel.convert_iter_to_child_iter(iter);
        self.model.remove(i_iter)
        self.conf.mark_changes()

    def check_cardnum(self,num, iter, selfiter, model):
        it = model.iter_children(iter)
        myname = model.get_value(selfiter,fid.name)
        while it is not None:
            if model.get_value(it,fid.name) == myname:
                it = model.iter_next(it)
                continue
            s_n = model.get_value(it,fid.xmlnode).prop("card")
            n = 0
            if s_n != None and s_n!="":
                n = int(s_n)

            if n == num:
                return it
            it = model.iter_next(it)
       
        return None 	  

    def check_baddr(self,baddr, iter, selfiter, model):
        it = model.iter_children(iter)
        myname = model.get_value(selfiter,fid.name)
        while it is not None:
            if model.get_value(it,fid.name) == myname:
                it = model.iter_next(it)
                continue
            s_n = model.get_value(it,fid.xmlnode).prop("baddr")
            n = 0
            if s_n != "" and s_n != None:
                n = int(eval(s_n))

            if n == baddr:
                return it
            it = model.iter_next(it)

    def on_edit_card_activate(self,menuitem):
        (model, iter) = self.tv.get_selection().get_selected()
        if not iter: return

        cnode = model.get_value(iter,fid.xmlnode)
        while True:
            res = self.editor.run(cnode)
            if res != dlg_RESPONSE_OK:
                return
            
            # check card number
            cnum = self.editor.card_num()
            it1 = self.check_cardnum(cnum,model.iter_parent(iter),iter,model)
            if it1 != None:
               msg = "card number='" + str(cnum) + "' " + _("already exist for %s") % model.get_value(it1,fid.name)
               dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
               res = dlg.run()
               dlg.hide()
               continue
            # check baddr
            s_baddr = self.editor.ba()
            baddr = 0
            if s_baddr != "":
                 baddr = int(eval(s_baddr))
            it1 = self.check_baddr(baddr,model.iter_parent(iter),iter,model)
            if baddr!=0 and it1 != None:
               msg = "base address='" + s_baddr + "' " + _("already exist for %s") % model.get_value(it1,fid.name)
               dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,msg)
               res = dlg.run()
               dlg.hide()
               continue

            break                

        
        self.editor.save(cnode)
     
        i_iter = self.fmodel.convert_iter_to_child_iter(iter)
        self.model.set_value(i_iter,fid.num,str(cnum))
        info  = 'card=' + str(cnode.prop("card"))
        info  = info + ' BA=' + str(cnode.prop("baddr"))
        self.model.set_value(i_iter,fid.param,info)
        self.update_card_info_for_sensors(i_iter,cnode)
        self.model.set_value(i_iter,fid.comm,cnode.prop("comment"))
        self.conf.mark_changes()

    def update_card_info_for_sensors(self,iter,cnode):

        # Идём по каналам
        it2 = self.model.iter_children(iter)
        cnum = self.model.get_value(iter,fid.num)
        while it2 is not None:
            snode = self.model.get_value(it2,fid.xmlnode)
            if snode != None:
               snode.setProp("card",cnum)
            it2 = self.model.iter_next(it2)

    def on_cb_lamp_toggled(self,btn):

        if btn.get_active():
           self.set_combobox_element(self.iotype,"AO")
           self.iotype.set_sensitive(False)
        else:
           self.iotype.set_sensitive(True)
           p_iter = self.model.iter_parent(self.myedit_iter)
           cardname = self.model.get_value(p_iter,fid.name)
           chan = self.model.get_value(self.myedit_iter,fid.num)
           subdev = self.model.get_value(self.myedit_iter,fid.subdev)
           iotype = self.ioconf.get_iotype(cardname,subdev,chan)
           if iotype == "":
              iotype = "DO"
           self.set_combobox_element(self.iotype,iotype)

    def on_edit_channel(self,iter):
        iter = self.fmodel.convert_iter_to_child_iter(iter)
        card_iter = self.model.iter_parent(iter)
        card = self.model.get_value(card_iter,fid.xmlnode)
        node_iter = self.model.iter_parent(card_iter)
        node = self.model.get_value(node_iter,fid.xmlnode)
        node_id = self.model.get_value(node_iter,fid.num) # node.prop("id")
        
        self.editor.card_init( card )

        self.sensor = self.model.get_value(iter,fid.xmlnode)
        snode = UniXML.EmptyNode()
        if self.sensor != None:
            snode = self.sensor
        else:
            # если добавление новой привязки
            # то выставляем значения настроек канала по умолчанию для данной карты
            def_params = self.ioconf.get_default_channel_param(card.prop("name"))
            if len(def_params) > 0:
               snode.setProp("aref",def_params["aref"])
               snode.setProp("range",def_params["range"])
            
        self.set_sensitive_pages()
        self.init_elements_value(self.channel_params,snode)

        if self.thr_lbl_aID.get_text() == "":
            self.tbl_tresholds.set_sensitive(False)
        else:
            self.tbl_tresholds.set_sensitive(True)

        prev_sensor = self.sensor
        txt = _("Setup ") + str(card.prop("name")) + ":" + str(self.model.get_value(iter,fid.name))
        self.dlg_info.set_text(txt)
        self.myedit_iter = iter

        cardname = self.model.get_value(card_iter,fid.name)
        chan = self.model.get_value(self.myedit_iter,fid.num)
        subdev = self.model.get_value(self.myedit_iter,fid.subdev)
        iotype = self.ioconf.get_iotype(cardname,subdev,chan)
        if iotype == "":
           # если у карты тип каналов не задан, берём непосредственно из конф. файла
           if snode:
              iotype = snode.prop("iotype")
           # если и в конф. файле не указан, делаем DI по умолчанию
           if iotype == "":
              iotype = "DI"
           self.iotype.set_sensitive(True)
        else:  
           # если у карты жёстко задан тип канала, то отключаем возможность менять
           self.iotype.set_sensitive(False)
           
        self.set_combobox_element(self.iotype,iotype)
        
        if iotype == "DI" or iotype == "AI":
           self.lamp.set_sensitive(False)
           self.lamp.set_active(False)
        else:
           self.lamp.set_sensitive(True)

        while True:
      
            if prev_sensor == None: 
               self.on_io_btn_sensor_clicked(None)
               if self.sensor == None:
                  return
        
            res = self.dlg_param.run()
            self.dlg_param.hide()
            if res != dlg_RESPONSE_OK:
                return

            # "очищаем старую привязку"
            if prev_sensor != self.sensor and prev_sensor is not None:
                self.save2xml_elements_value(self.io_params,prev_sensor,"")

            if self.sensor == None: # "очищаем старую привязку"
                self.model.set_value(iter,fid.xmlnode,None)
                self.model.set_value(iter,fid.param,"")
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

        if self.sensor != prev_sensor: # "очищаем старую привязку"
           if prev_sensor != None and prev_sensor is not None:
              self.save2xml_elements_value(self.io_params,prev_sensor,"")
           self.model.set_value(iter,fid.xmlnode,None)
           self.model.set_value(iter,fid.param,"")
           self.myedit_iter = None
           self.conf.mark_changes()

        if self.sensor == None:
           return

        self.myedit_iter = None
        
        # Сохраняем параметры
        self.model.set_value(iter,fid.xmlnode,self.sensor)
        self.model.set_value(iter,fid.param,self.get_sensor_info(self.sensor))
        self.sensor.setProp("io",node_id)
        self.sensor.setProp("card",card.prop("card"))
        self.sensor.setProp("subdev", str(self.model.get_value(iter,fid.subdev)))
        self.sensor.setProp("channel",str(self.model.get_value(iter,fid.num)))
        # Остальные параметры по списку
        self.save2xml_elements_value(self.channel_params,self.sensor)
        self.conf.mark_changes()
  
    def get_node_info(self, xmlnode):
        return str("id=" + str(xmlnode.prop("id")) + " ip=" + xmlnode.prop("ip"))

    def get_sensor_info(self, xmlnode):
        return "[%s]%s"%(xmlnode.prop("id"),xmlnode.prop("name"))

    def nodeslist_change(self,obj, xmlnode):
        node_id = xmlnode.prop("name")
        # Ищем узел проходим по всем его картам и датчикам
        # и подменяем io="old_id" на io="new_id"
        it = self.model.get_iter_first()
        while it is not None:
            if self.model.get_value(it,2) == xmlnode:
                # заодно обновляем параметры
                self.model.set_value(it,fid.num,xmlnode.prop("name"))
                self.model.set_value(it,fid.name,xmlnode.prop("name")) 
                self.model.set_value(it,fid.param,self.get_node_info(xmlnode))
                it1 = self.model.iter_children(it)
                # Идём по картам
                while it1 is not None:
                    it2 = self.model.iter_children(it1)
                    # Идём по каналам 
                    while it2 is not None:
                        snode = self.model.get_value(it2,fid.xmlnode)
                        if snode != None:
                            snode.setProp("io",node_id)
                        it2 = self.model.iter_next(it2)
                   
                    it1 = self.model.iter_next(it1)
                self.conf.mark_changes()
                break
           
            it = self.model.iter_next(it)
    
    def nodeslist_add(self,obj, xmlnode):
        img = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_NODE)
        self.model.append(None,[xmlnode.prop("name"),self.get_node_info(xmlnode),xmlnode,"node",xmlnode.prop("name"),"0",img,xmlnode.prop("comment")])
    
    def nodeslist_remove(self,obj, xmlnode):
        node_id = xmlnode.prop("name")
        # Ищем узел проходим по всем его картам и датчикам
        # и удаляем io="id"
        it = self.model.get_iter_first()
        dlg_ok = False
        while it is not None:
            if self.model.get_value(it,2) == xmlnode:
                it1 = self.model.iter_children(it)
                # Идём по картам
                while it1 is not None:
                    it2 = self.model.iter_children(it1)
                    # Идём по каналам 
                    while it2 is not None:
                        snode = self.model.get_value(it2,fid.xmlnode)
                        if snode != None:
                             # Спрашиваем только на первой встретившейся "привязке" датчика
                             if dlg_ok == False:
                                 msg = _("Remove io configuration for sensors at node='") + str(xmlnode.prop("name")) + "'"
                                 dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,msg)
                                 res = dlg.run()
                                 dlg.hide()
                                 if res == gtk.RESPONSE_NO:
                                      return
                                 dlg_ok = True
                            
                             snode.setProp("io","")
                             snode.setProp("card","")
                             snode.setProp("subdev","")
                             snode.setProp("channel","")
                        it2 = self.model.iter_next(it2)
                   
                    it1 = self.model.iter_next(it1)
                
                self.model.remove(it)
                self.conf.mark_changes()
                break
           
            it = self.model.iter_next(it)

    def on_gen_comediconf_activate(self,menuitem):
        
        (model, iter) = self.tv.get_selection().get_selected()
        if not iter: return
        
        t = model.get_value(iter,fid.etype)
        node_iter = None
        if t == "card":
            node_iter = model.iter_parent(iter)
        elif t == "node":
            node_iter = iter
        else:
            print "*** FAILED ELEMENT TYPE " + t
            return
        
        xmlnode = model.get_value(node_iter,fid.xmlnode)
        
        cardnode = self.conf.xml.findNode(xmlnode,"iocards")[0]
        if cardnode == None or cardnode.children.next == None:
            print "<iocards> not found for node='%s'" % xmlnode.prop("name")
            return
        cardnode = cardnode.children.next

        dlg = gtk.FileChooserDialog(_("File save"),action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        
        outfile = self.ioconf.get_outfilename(xmlnode)
        dlg.set_current_name(outfile)
        res = dlg.run()
        dlg.hide()
        
        if res == gtk.RESPONSE_OK:
           self.ioconf.gen_comedi_script(cardnode,dlg.get_filename())

    def find_str(self, s1, s2, case):

        if s1 == None or s2 == None:
           return False

        if case == False:
           if s1.upper().find(s2.upper()) != -1:
                return True
           return False

        if s1.find(s2) != -1:
             return True

        return False

    def filter_entry_changed(self,entry):
        self.fmodel.refilter()

    def filter_cb_toggled(self,checkbtn):
        self.fmodel.refilter()
             
    def view_filter_func(self, model, it):

        if it == None:
           return True

        t = self.fentry.get_text()
        if t == "":
             return True

        etype = model.get_value(it,fid.etype)
        if etype == "channel":
           xmlnode = model.get_value(it,fid.xmlnode)

           # если привязки ещё нет, то не отображаем
           if xmlnode == None:
              return False

           # если имя датчика "пустое"(то тоже  не отображаем)
           sname = str(xmlnode.prop("name"))
           if sname == "":
              return False

           ok = self.find_str(sname, t, self.filter_cb_case.get_active())

           # раскрываем те деревья, где найден датчика
           path = model.get_path(it)
           self.tv.expand_to_path(path)
           return ok
           

        return True


    def btn_collaps_clicked(self,btn):
        self.tv.collapse_all()


def create_module(conf):
    return IOEditor(conf)

def module_name():
    return "Ввод/вывод"
