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
        self.module_name = ""

    def get_supported_cards( self ):
        return []

    def check_support( self, cname ):
        if cname.upper() in self.get_supported_cards():
           return True

        return False

    def get_module_name(self):
        return self.module_name

    def get_module_params(self,cnode):
        return ""

    def get_name(self):
        return editor_name()

    def get_face( self ):
        return self.builder.get_object("main")

    def build_channel_list( self, cname ):
        return [[0,"Unknown card","",0]]

    def default_init(self,cname):
        pass

    def init(self,cname,editor_ui,xmlnode):
        self.simple_init(cname,editor_ui,xmlnode)

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

    def save(self,xmlnode,cname):
        self.simple_save(xmlnode,cname)

    def delete(self,xmlnode,cname):
        pass

    def simple_save( self, xmlnode, cname ):
        self.save2xml_elements_value(self.params,xmlnode)

    def get_channel_list( self, cname ):
        return self.build_channel_list(cname.upper())
        
    def get_iotype( self, cname, subdev, channel ):
        clist = self.get_channel_list(cname)
        subdev = to_int(subdev)
        channel = to_int(channel)
        for c in clist:
            if c[cid.cnum] == channel and c[cid.subdev] == subdev:
               return c[cid.iotype]

        return ""

    def get_default_channel_param(self,cname):
        ret = dict()
        ret["aref"] = 0
        ret["range"] = 0
        return ret


def editor_name():
    return ""