# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_editor
from global_conf import *
import dlg_xlist

class SESProcess(base_editor.BaseEditor):

    def __init__(self, conf):

        base_editor.BaseEditor.__init__(self,conf)

        self.builder = gtk.Builder()
        self.builder.add_from_file(conf.datdir+"ses_process.ui")
        self.builder.connect_signals(self)

        self.props = []
        for o in self.builder.get_objects():
            if o.__class__.__name__ == "Entry":
               name = gtk.Buildable.get_name(o)
               self.props.append([name,name,name,True])
               #print "ADD: %s"%gtk.Buildable.get_name(o)
        self.init_builder_elements(self.props,self.builder)
  
        self.elements=[
            ["win","main_window",None,False],
            ["entName","entName",None,False]
        ]
        self.init_builder_elements(self.elements,self.builder)

    def run(self, xmlnode):
        #print "PANEL NODE: %s"%str(xmlnode)
        self.init_elements_value(self.props,xmlnode)
        res = self.win.run()
        self.win.hide()
        if res != dlg_RESPONSE_OK:
           return False

        self.save2xml_elements_value(self.props,xmlnode)
        xmlnode.setProp("name", self.entName.get_text())
        return True
    
    def on_select_clicked( self, btn ):
        #print "SELECT CLICKED..btn-name=%s"%str(btn.name)
        #print "*** name=%s"%gtk.Buildable.get_name(btn)
        btn_name = gtk.Buildable.get_name(btn)
        ent_name = btn_name[:-4]  # remove "_btn" postfix
        ent = self.builder.get_object(ent_name)
        if not ent:
           print "%s not found in ui-file"%ent_name
           return

        xmlnode = ent.get_data("xmlnode")
        txt = to_str(ent.get_text())
        if txt != "":
            xmlnode = self.conf.s_dlg().set_selected_name(txt)

        s = self.conf.s_dlg().run(self,xmlnode)
        if s != None:
            ent.set_text(to_str(s.prop("name")))
            ent.set_data("xmlnode",s)
        else:
            ent.set_text("")
            ent.set_data("xmlnode",None)
		