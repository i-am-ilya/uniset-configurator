# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import simple_card
from global_conf import *

class Card_AIxx5a(simple_card.SimpleCard):

    def __init__(self,datdir,uifile="card_AIxx5a.ui"):

        simple_card.SimpleCard.__init__(self,datdir,uifile)

        self.cname = "AIxx5a"

        self.params=[
            ["avg","cbox_avg","avg",False]
        ]
        self.init_builder_elements(self.params,self.builder)

        self.module_name = "aixx5a"
        self.default_init(self.cname)

    def get_supported_cards( self ):
        return ["AIC120","AIC121","AIC123XX","AI16-5A-3"]

    def build_channel_list( self, cname ):
        clist=[]
        for i in range(0,8):
            clist.append([i,"J2:"+str(i),"AI",2])
        for i in range(8,16):
            clist.append([i,"J3:"+str(i-8),"AI",2])
        for i in range(0,2):
            clist.append([i,"AO:"+str(i),"AO",1])

        return clist

    def default_init(self,cname):
        self.avg.set_active(0)

    def aixx5a_init( self, cname, editor_ui, xmlnode ):
        self.simple_init(cname,editor_ui,xmlnode)
        self.on_cbox_avg_changed(self.avg)

    def init( self, cname, editor_ui, xmlnode ):
        self.aixx5a_init(cname,editor_ui,xmlnode)

    def save( self, xmlnode, cname ):
        self.simple_save(xmlnode,cname)

    def delete(self,xmlnode,cname):
        xmlnode.setProp("avg","")

    def get_params(self,cname,avg):
        p = ""
        if self.cname == "AIC120" or self.cname == "AIC121":
           p="0"
        elif self.cname == "AIC123XX" or cname == "AI16-5A-3":
           p="1"
        else:
           p="0"

        if avg == None:
           avg="1"

        s = "%s,%s"%(p,to_str(avg))
        return s

    def get_module_params(self,cnode):
        return self.get_params(cnode.prop("name"),cnode.prop("avg"))

    def on_cbox_avg_changed(self,cb):

        if self.editor_ui == None:
           return

        s = self.get_params(self.cname,self.avg.get_active_text())
        ent_mod_param  = self.editor_ui.get_object("io_params")
        ent_mod_param.set_text(s)

    def get_default_channel_param(self,cname):
        ret = dict()
        ret["aref"] = 2
        ret["range"] = 0
        return ret

def create_editor(datdir):
    return Card_AIxx5a(datdir)

def editor_name():
    return "Card_AIxx5a"