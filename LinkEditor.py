# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import pango
import gobject
import UniXML
import libxml2
import configure
import base_editor
from global_conf import *
import dlg_xlist

pic_BTN = 'btn.png'
pic_FAIL = 'link_error.png'
pic_WARN= 'link_warning.png'
pic_OK = 'link_ok.png'

class fid():
   value = 0
   name = 1
   vartype = 2
   iotype = 3
   comm = 4
   bg = 5
   xmlnode = 6
   img = 7
   itype = 8
   nocheckid = 9
   v_min = 10
   v_max = 11
   v_def = 12


class LinkEditor(base_editor.BaseEditor):

    def __init__(self, conf, source_file=""):

        base_editor.BaseEditor.__init__(self,conf)

        self.builder = gtk.Builder()
        self.builder.add_from_file(conf.datdir+"LinkEditor.ui")
        self.builder.connect_signals(self)

        self.elements=[
            ["win","main_window",None,False],
            ["menu","menubar1",None,False],
            ["main_book","main_book",None,False],
            ["entName","entName",None,False],
            ["tv","main_treeview",None,False],
            ["tv_msg","msg_treeview",None,False],
            ["tv_addon","addon_treeview",None,False],
            ["dlg_val","dlg_val",None,False],
            ["val_spn","val",None,False],
            ["val_comm","val_lblComm",None,False],
            ["val_name","val_lblName",None,False],
            ["val_adj","adj1",None,False],
            ["dlg_str","dlg_str",None,False],
            ["val_str","val_str",None,False],
            ["dlg_bool","dlg_bool",None,False],
            ["val_bool","cb_bool",None,False]
            
        ]
        self.init_builder_elements(self.elements,self.builder)
        #self.model = self.tv.get_model()
        self.model = gtk.ListStore(
                              gobject.TYPE_STRING,  # value
                              gobject.TYPE_STRING,  # name
                              gobject.TYPE_STRING,  # vartype
                              gobject.TYPE_STRING,  # iotype
                              gobject.TYPE_STRING,  # comm
                              gobject.TYPE_STRING,  # bg_color
                              object,               # xmlnode
                              gtk.gdk.Pixbuf,       # picture
                              gobject.TYPE_STRING,  # item type
                              gobject.TYPE_BOOLEAN)    # no_check_id 

        self.msg_model = gtk.ListStore(
                              gobject.TYPE_STRING,  # value
                              gobject.TYPE_STRING,  # name
                              gobject.TYPE_STRING,  # vartype
                              gobject.TYPE_STRING,  # iotype
                              gobject.TYPE_STRING,  # comm
                              gobject.TYPE_STRING,  # bg_color
                              object,               # xmlnode
                              gtk.gdk.Pixbuf,       # picture
                              gobject.TYPE_STRING,  # item type
                              gobject.TYPE_BOOLEAN)    # no_check_id 
                              
        self.addon_model = gtk.ListStore(
                              gobject.TYPE_STRING,  # value
                              gobject.TYPE_STRING,  # name
                              gobject.TYPE_STRING,  # vartype
                              gobject.TYPE_STRING,  # iotype
                              gobject.TYPE_STRING,  # comm
                              gobject.TYPE_STRING,  # bg_color
                              object,               # xmlnode
                              gtk.gdk.Pixbuf,       # picture
                              gobject.TYPE_STRING,  # item type
                              gobject.TYPE_BOOLEAN,    # no_check_id
                              gobject.TYPE_STRING,  # min
                              gobject.TYPE_STRING,  # max
                              gobject.TYPE_STRING)  # default value

        self.tv.set_model(self.model)
        self.tv.connect("button-press-event", self.on_btn_press_event, self.tv)

        self.tv_msg.set_model(self.msg_model)
        self.tv_msg.connect("button-press-event", self.on_btn_press_event, self.tv_msg)

        self.tv_addon.set_model(self.addon_model)
        self.tv_addon.connect("button-press-event", self.on_addon_press_event, self.tv_addon)

        self.img_ok = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_OK)
        self.img_fail = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_FAIL)
        self.img_warning = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_WARN)

        if source_file != "":
           self.build_editor(source_file)

    def build_editor(self,sfile):
        try:
            doc = libxml2.parseFile(sfile)
        except libxml2.parserError:
            print 'File "%s" parse error' % cfg
            raise Exception()

        ctxt = doc.xpathNewContext()
        res = ctxt.xpathEval("//smap/*")

        for i in res:
            nocheckid = False
            if i.prop("no_check_id") == "1":
               nocheckid = True

            #print i.prop("name")
            if i.name == "item":
               self.model.append(["",i.prop("name"),i.prop("vartype"),i.prop("iotype"),i.prop("comment"),None,None,None,"item",nocheckid])
            elif i.name == "group":
               self.model.append(["",i.prop("name"),i.prop("vartype"),i.prop("iotype"),i.prop("comment"),"gray",None,None,"group",True])

        res = ctxt.xpathEval("//msgmap/*")

        for i in res:
            #print i.prop("name")
            if i.name == "item":
               self.msg_model.append(["",i.prop("name"),"","",i.prop("comment"),None,None,None,"item",True])
            elif i.name == "group":
               self.msg_model.append(["",i.prop("name"),"","",i.prop("comment"),"gray",None,None,"group",True])

        res = ctxt.xpathEval("//variables/*")
        for i in res:
            #print i.prop("name")
            if i.name == "item":
               self.addon_model.append(["",i.prop("name"),i.prop("type"),"",i.prop("comment"),None,None,None,"item",True,
                   i.prop("min"),i.prop("max"),i.prop("default")
                  ])
            elif i.name == "group":
               self.addon_model.append(["",i.prop("name"),i.prop("type"),"",i.prop("comment"),"gray",None,None,"group",True,"","",""])


    def get_face(self):
        return self.main_book

    def init_tree(self, model, xmlnode, check=False):
        it = model.get_iter_first()
        while it is not None:
            val = to_str( xmlnode.prop(model.get_value(it,fid.name)) )
            model.set_value(it,fid.value,val)
            itype = model.get_value(it,fid.itype)
            nocheckid =  model.get_value(it,fid.nocheckid)
            if val != "" and itype == "item" and check == True:
               if self.conf.find_sensor(val) == None:
                  model.set_value(it,fid.img,self.img_fail)
               else:
                  model.set_value(it,fid.img,self.img_ok)
            elif check == True and val == "" and nocheckid == False:
                 model.set_value(it,fid.img,self.img_warning)

            it = model.iter_next(it)

    def pre_init(self, xmlnode):
        self.init_tree(self.tv.get_model(),xmlnode,True)
        self.init_tree(self.tv_msg.get_model(),xmlnode,True)
        self.init_tree(self.tv_addon.get_model(),xmlnode,False)
        self.entName.set_text( to_str(xmlnode.prop("name")) )
        
    def run(self, xmlnode, showMenu = False):

        if showMenu:
           self.menu.show()
        else:
           self.menu.hide()

        self.xmlnode = xmlnode
        self.pre_init(xmlnode)
        res = self.win.run()
        self.win.hide()
        if res != dlg_RESPONSE_OK:
           return False

        self.conf.mark_changes()
        self.xmlnode = None
        return self.save(xmlnode)

    def save(self,xmlnode):
        self.save2xml(self.tv.get_model(),xmlnode)
        self.save2xml(self.tv_msg.get_model(),xmlnode)
        self.save2xml(self.tv_addon.get_model(),xmlnode)
        xmlnode.setProp("name", self.entName.get_text())
        return True

    def save2xml(self, model, xmlnode):
        it = model.get_iter_first()
        while it is not None:
            xmlnode.setProp(model.get_value(it,fid.name),model.get_value(it,fid.value))
            it = model.iter_next(it)

    def on_save( self, mi ):
        if self.xmlnode:
           self.save(self.xmlnode)
           self.conf.xml.save(None,True,True)
           self.conf.unmark_changes()

    def on_reload( self, mi ):
        if self.conf.is_changed():
           dlg = gtk.MessageDialog(self.win, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO, _("Save changes?"))
           res = dlg.run()
           dlg.hide()
           if res == gtk.RESPONSE_YES:
              self.save(self.xmlnode)
              self.conf.xml.save(None,True,True)
           self.conf.unmark_changes()

        oname = self.xmlnode.prop("name")
        cname = self.xmlnode.name
        self.conf.reopen(self.conf.xml.fname)
        self.xmlnode = self.conf.xml.findNode_byPropValue(self.conf.xml.getDoc(),cname,oname,"name",True)[0]
        if self.xmlnode:
           self.pre_init(self.xmlnode)

    def on_quit( self, mi ):
        if self.conf.is_changed():
            dlg = gtk.MessageDialog(self.win, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO, _("Save changes?"))
            res = dlg.run()
            dlg.hide()
            if res == gtk.RESPONSE_YES:
               self.win.response(dlg_RESPONSE_OK)
               return

        self.win.response(gtk.RESPONSE_NO)
    
    def on_btn_press_event(self, object, event, tv):
        (model, iter) = tv.get_selection().get_selected()

        if event.button == 3:
            if not iter:
               return False

        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
           if not iter:
              return False
           self.on_select_clicked(tv.get_model(),iter)

        return False

    def on_select_clicked( self, model, iter ):
        
        txt = model.get_value(iter,fid.value)
        xmlnode = self.conf.s_dlg().set_selected_name(txt)

        s = self.conf.s_dlg().run(self,xmlnode)
        if s != xmlnode:
           self.conf.mark_changes()

        if s != None:
        
            if model.get_value(iter,fid.iotype).upper() != s.prop("iotype").upper():
               msg = "Тип выбранного датчика '%s' не совпадает с типом для этого поля '%s'\nВсё равно сохранить?"%(s.prop("iotype").upper(),model.get_value(iter,fid.iotype).upper())
               dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,msg)
               res = dlg.run()
               dlg.hide()
               if res == gtk.RESPONSE_NO:
                  return

            model.set_value(iter,fid.value,to_str(s.prop("name")))
            model.set_value(iter,fid.xmlnode,s)
            model.set_value(iter,fid.img,self.img_ok)
        else:
            model.set_value(iter,fid.value,"")
            model.set_value(iter,fid.xmlnode,None)
            if model.get_value(iter,fid.nocheckid) == False:
               model.set_value(iter,fid.img,self.img_warning)
            else:
               model.set_value(iter,fid.img,None)

    def on_addon_press_event(self, object, event, tv):
        (model, iter) = tv.get_selection().get_selected()

        if event.button == 3:
            if not iter:
               return False

        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
           if not iter:
              return False

           xmlnode = model.get_value(iter,fid.xmlnode)
           etype = model.get_value(iter,fid.vartype)

           if etype == "int" or etype == "float":
              v_max = 100000000
              v_min = -v_max
              mi = to_str(model.get_value(iter,fid.v_min))
              ma = to_str(model.get_value(iter,fid.v_max))
              if ma:
                 if etype == "int":
                    v_max = to_int(ma)
                 else:
                    v_max = to_float(ma)
              if mi:
                 if etype == "int":
                    v_min = to_int(mi)
                 else:
                    v_min = to_float(mi)

              self.val_adj.set_upper(v_max)
              self.val_adj.set_lower(v_min)
              self.val_name.set_text(model.get_value(iter,fid.name))
              if etype == "int":
                 self.val_spn.set_digits(0)
              else:
                 self.val_spn.set_digits(3)
              
              self.val_spn.set_value( to_float(model.get_value(iter,fid.value)) )
              txt = ""
              if mi!="" and ma!="":
                 txt = "Введите число от %s до %s"%(mi,ma)
              elif mi!="":
                 txt = "Введите число больше %s"%(mi)
              elif ma!="":
                 txt = "Введите число меньше %s"%(ma)

              self.val_comm.set_text(txt)
              res = self.dlg_val.run()
              self.dlg_val.hide()
              if res != dlg_RESPONSE_OK:
                 return False

              if etype == "int":
                 model.set_value(iter,fid.value, to_str(self.val_spn.get_value_as_int()) )
              else:
                 model.set_value(iter,fid.value, to_str(self.val_spn.get_value()))

              return False
          
           elif etype == "str":
              self.val_str.set_text(model.get_value(iter,fid.value))
              res = self.dlg_str.run()
              self.dlg_str.hide()
              if res != dlg_RESPONSE_OK:
                 return False

              model.set_value(iter,fid.value,self.val_str.get_text())
              return False

           elif etype == "bool":
              self.val_bool.set_active( to_int(model.get_value(iter,fid.value)) )
              self.val_bool.set_label(model.get_value(iter,fid.name))
              res = self.dlg_bool.run()
              self.dlg_bool.hide()
              if res != dlg_RESPONSE_OK:
                 return False

              v = "0"
              if self.val_bool.get_active():
                 v = "1"
              model.set_value(iter,fid.value,v)
              return False

           elif etype == "sensor":
              txt = model.get_value(iter,fid.value)
              xmlnode = self.conf.s_dlg().set_selected_name(txt)
              s = self.conf.s_dlg().run(self,xmlnode)
              if s != None:
                 model.set_value(iter,fid.value,to_str(s.prop("name")))
              else:
                 model.set_value(iter,fid.value,"")

        return False

def create_module(conf):
    return LinkEditor(conf)

def module_name():
    return "Редактор связей"
