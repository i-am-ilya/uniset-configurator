# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import simple_card
from global_conf import *

class Card_DI32(simple_card.SimpleCard):

    def __init__(self,datdir,uifile="card_DI32.ui"):

        simple_card.SimpleCard.__init__(self,datdir,uifile)

        self.cname = "DI32"
        self.clist = self.build_channel_list(self.cname)
        self.params=[
            ["jar","cbox_jartime","jar",False]
        ]
        self.init_builder_elements(self.params,self.builder)        

        self.node_xmlnode = None
        self.editor_ui = None

        self.module_name = "di32_5"
        self.default_init(self.cname)

    def get_supported_cards( self ):
        return ["DI32"]

    def default_init(self,cname):
        self.jar.set_active(0)

    def init( self, cname, editor_ui, xmlnode ):
        self.simple_init(cname,editor_ui,xmlnode)
        if xmlnode:
           self.set_combobox_element(self.jar,xmlnode.prop("jar"),1)

        self.on_cbox_jar_changed(self.jar)

    def build_channel_list( self, cname ):
        clist=[]
        for i in range(0,16):
            clist.append([i,"J1:"+str(i),"DI",0])
        for i in range(16,32):
            clist.append([i,"J2:"+str(i-16),"DI",0])

        return clist

    def get_params(self,cnode):
        return to_str(cnode.prop("jar"))

    def on_cbox_jar_changed(self,cb):

        if self.editor_ui == None:
           return

        s = self.jar.get_model().get_value(self.jar.get_active_iter(),1)
        ent_mod_param  = self.editor_ui.get_object("io_params")
        ent_mod_param.set_text(s)

def create_editor(datdir):
    return Card_DI32(datdir)

def editor_name():
    return "Card_DI32"
