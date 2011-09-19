# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import simple_card
from global_conf import *

class Card_KM5856(simple_card.SimpleCard):

    def __init__(self,datdir,uifile="card_None.ui"):

        simple_card.SimpleCard.__init__(self,datdir,uifile)

        self.cname = "KM5856"
        self.clist = self.build_channel_list(self.cname)

        self.module_name = "km5856"
        self.default_init(self.cname)

    def get_supported_cards( self ):
        return ["KM5856"]

    def build_channel_list( self, cname ):
        clist=[]
        for i in range(0,16):
            clist.append([i,"DI:"+str(i),"DI",0])
        for i in range(0,16):
            clist.append([i,"DO:"+str(i),"DO",1])

        return clist

    def get_module_params(self,cnode):
        return ""

def create_editor(datdir):
    return Card_KM5856(datdir)

def editor_name():
    return "Card_KM5856"