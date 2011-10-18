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

class LinkEditor(base_editor.BaseEditor):

    def __init__(self, conf, source_file=""):

        base_editor.BaseEditor.__init__(self,conf)

        self.builder = gtk.Builder()
        self.builder.add_from_file(conf.datdir+"LinkEditor.ui")
        self.builder.connect_signals(self)

        self.elements=[
            ["win","main_window",None,False],
            ["tv","main_treeview",None,False]
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

        self.tv.set_model(self.model)
        self.tv.connect("button-press-event", self.on_button_press_event)

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

    def run(self, xmlnode):

        it = self.model.get_iter_first()
        while it is not None:
            val = to_str( xmlnode.prop(self.model.get_value(it,fid.name)) )
            self.model.set_value(it,fid.value,val)
            it = self.model.iter_next(it)  
        
        res = self.win.run()
        self.win.hide()
        if res != dlg_RESPONSE_OK:
           return False

        it = self.model.get_iter_first()
        while it is not None:
            xmlnode.setProp(self.model.get_value(it,fid.name),self.model.get_value(it,fid.value))
            it = self.model.iter_next(it)  

        xmlnode.setProp("name", self.entName.get_text())
        return True

    def on_button_press_event(self, object, event):
        (model, iter) = self.tv.get_selection().get_selected()

        if event.button == 3:
            if not iter:
               return False

        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
           if not iter:
              return False
           self.on_select_clicked(iter)

        return False

    def on_select_clicked( self, iter ):
        
        txt = self.model.get_value(iter,fid.value)
        xmlnode = self.conf.s_dlg().set_selected_name(txt)

        s = self.conf.s_dlg().run(self,xmlnode)
        if s != None:
            self.model.set_value(iter,fid.value,to_str(s.prop("name")))
            self.model.set_value(iter,fid.xmlnode,s)
        else:
            self.model.set_value(iter,fid.value,"")
            self.model.set_value(iter,fid.xmlnode,None)
		