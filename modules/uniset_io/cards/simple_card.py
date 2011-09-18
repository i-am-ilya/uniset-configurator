# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import base_editor
from global_conf import *

class cid():
  cnum = 0
  cname = 1
  iotype = 2
  subdev = 3

  
class SimpleCard(base_editor.BaseEditor):

    def __init__(self,datdir,uifile):

        base_editor.BaseEditor.__init__(self,"")
        self.builder = gtk.Builder()
        uifile = datdir+uifile
        self.builder.add_from_file(uifile)
        self.builder.connect_signals(self)

        self.node_xmlnode = None
        self.editor_ui = None
        self.params = []

    def get_supported_cards( self ):
        return []

    def check_support( self, cname ):
        if cname.upper() in self.get_supported_cards():
           return True

        return False

    def get_name(self):
        editor_name()

    def get_face( self ):
        return self.builder.get_object("main")

    def build_channel_list( self, cname ):
        return [[0,"Unknown card","DI",0]]

    def default_init(self,cname):
        pass

    def simple_init( self, cname, editor_ui, xmlnode ):
 
        self.editor_ui = editor_ui
        ent_mod_name  = editor_ui.get_object("io_module")
        ent_mod_param  = editor_ui.get_object("io_params")

        ent_mod_name.set_text(self.module_name)
        ent_mod_param.set_text("")
        self.cname = cname

        if xmlnode:
           self.init_elements_value(self.params,xmlnode)
        else:
           self.default_init(cname)

    def simple_save( self, xmlnode, cname ):
        self.save2xml_elements_value(self.params,xmlnode)

    def get_channel_list( self, cname ):
        if cname.upper() != self.cname.upper():
           self.clist = self.build_channel_list(cname.upper())

        return self.clist
        
    def get_iotype( self, channel ):
        nchan = to
        for c in self.clist:
            if c[cid.cnum] == channel:
               return c[cid.iotype]

        return "DI"


def editor_name():
    return ""