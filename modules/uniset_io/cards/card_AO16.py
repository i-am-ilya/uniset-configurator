# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import simple_card
from global_conf import *

class Card_AO16(simple_card.SimpleCard):

    def __init__(self,datdir,uifile="card_None.ui"):

        simple_card.SimpleCard.__init__(self,datdir,uifile)

        self.cname = "AO16"

        self.module_name = "ao16"
        self.default_init(self.cname)

    def get_supported_cards( self ):
        return ["AO16-XX"]

    def build_channel_list( self, cname ):
        clist=[]
        for i in range(0,8):
            clist.append([i,"(%2d) J1:%d"%(i,i),"AO",0])
        for i in range(8,16):
            clist.append([i,"(%2d) J2:%d"%(i,i-8),"AO",0])

        return clist

    def get_module_params(self,cnode):
        return ""

def create_editor(datdir):
    return Card_AO16(datdir)

def editor_name():
    return "Card_AO16"
    