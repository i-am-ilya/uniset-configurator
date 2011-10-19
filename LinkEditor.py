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

class fid():
   value = 0
   name = 1
   vartype = 2
   iotype = 3
   comm = 4
   bg = 5
   xmlnode = 6
   v_min = 7
   v_max = 8
   v_def = 9

class LinkEditor(base_editor.BaseEditor):

    def __init__(self, conf, source_file=""):

        base_editor.BaseEditor.__init__(self,conf)

        self.builder = gtk.Builder()
        self.builder.add_from_file(conf.datdir+"LinkEditor.ui")
        self.builder.connect_signals(self)

        self.elements=[
            ["win","main_window",None,False],
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
                              object)  # xmlnode

        self.msg_model = gtk.ListStore(
                              gobject.TYPE_STRING,  # value
                              gobject.TYPE_STRING,  # name
                              gobject.TYPE_STRING,  # vartype
                              gobject.TYPE_STRING,  # iotype
                              gobject.TYPE_STRING,  # comm
                              gobject.TYPE_STRING,  # bg_color
                              object)  # xmlnode

        self.addon_model = gtk.ListStore(
                              gobject.TYPE_STRING,  # value
                              gobject.TYPE_STRING,  # name
                              gobject.TYPE_STRING,  # vartype
                              gobject.TYPE_STRING,  # iotype
                              gobject.TYPE_STRING,  # comm
                              gobject.TYPE_STRING,  # bg_color
                              object,  # xmlnode
                              gobject.TYPE_STRING,  # min
                              gobject.TYPE_STRING,  # max
                              gobject.TYPE_STRING)  # default value

        self.tv.set_model(self.model)
        self.tv.connect("button-press-event", self.on_btn_press_event, self.tv)

        self.tv_msg.set_model(self.msg_model)
        self.tv_msg.connect("button-press-event", self.on_btn_press_event, self.tv_msg)

        self.tv_addon.set_model(self.addon_model)
        self.tv_addon.connect("button-press-event", self.on_addon_press_event, self.tv_addon)

        if source_file != "":
           self.build_editor(source_file)

    def build_editor(self,sfile):
        try:
            doc = libxml2.parseFile(sfile)
        except libxml2.parserError:
            raise CommandError('File "%s" parse error' % cfg)		

        ctxt = doc.xpathNewContext()
        res = ctxt.xpathEval("//smap/*")

        for i in res:
            #print i.prop("name")
            if i.name == "item":
               self.model.append(["",i.prop("name"),i.prop("vartype"),i.prop("iotype"),i.prop("comment"),None,None])
            elif i.name == "group":
               self.model.append(["",i.prop("name"),i.prop("vartype"),i.prop("iotype"),i.prop("comment"),"gray",None])

        res = ctxt.xpathEval("//msgmap/*")

        for i in res:
            #print i.prop("name")
            if i.name == "item":
               self.msg_model.append(["",i.prop("name"),"","",i.prop("comment"),None,None])
            elif i.name == "group":
               self.msg_model.append(["",i.prop("name"),"","",i.prop("comment"),"gray",None])

        res = ctxt.xpathEval("//params/*")
        for i in res:
            #print i.prop("name")
            if i.name == "item":
               self.addon_model.append(["",i.prop("name"),i.prop("type"),"",i.prop("comment"),None,None,
                   i.prop("min"),i.prop("max"),i.prop("default")
                  ])
            elif i.name == "group":
               self.addon_model.append(["",i.prop("name"),i.prop("type"),"",i.prop("comment"),"gray",None,"","",""])

    def init_tree(self, model, xmlnode):
        it = model.get_iter_first()
        while it is not None:
            val = to_str( xmlnode.prop(model.get_value(it,fid.name)) )
            model.set_value(it,fid.value,val)
            it = model.iter_next(it)

    def run(self, xmlnode):

        self.init_tree(self.tv.get_model(),xmlnode)
        self.init_tree(self.tv_msg.get_model(),xmlnode)
        self.init_tree(self.tv_addon.get_model(),xmlnode)
        self.entName.set_text( to_str(xmlnode.prop("name")) )
        
        res = self.win.run()
        self.win.hide()
        if res != dlg_RESPONSE_OK:
           return False

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
        if s != None:
            model.set_value(iter,fid.value,to_str(s.prop("name")))
            model.set_value(iter,fid.xmlnode,s)
        else:
            model.set_value(iter,fid.value,"")
            model.set_value(iter,fid.xmlnode,None)

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

        return False
