# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import simple_card
from global_conf import *

class Card_KM5901(simple_card.SimpleCard):

    def __init__(self,datdir,uifile="card_None.ui"):

        simple_card.SimpleCard.__init__(self,datdir,uifile)

        self.cname = "KM5901"

        self.module_name = "km5901"
        self.default_init(self.cname)

    def get_supported_cards( self ):
        return ["KM5901"]

    def build_channel_list( self, cname ):
        clist=[]
        for i in range(0,48):
            clist.append([i,"(%2d) X1:%d"%(i,i),"DI",0])
        for i in range(48,96):
            clist.append([i,"(%2d) X2:%d"%(i,i-48),"DI",0])

        return clist

    def get_module_params(self,cnode):
        return ""

def create_editor(datdir):
    return Card_KM5901(datdir)

def editor_name():
    return "Card_KM5901"