# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import simple_card
from global_conf import *

class Card_PCI1750(simple_card.SimpleCard):

    def __init__(self,datdir,uifile="card_None.ui"):

        simple_card.SimpleCard.__init__(self,datdir,uifile)

        self.cname = "PCI-1750"

        self.module_name = "adv_pci1750"
        self.default_init(self.cname)

    def get_supported_cards( self ):
        return ["Advantech PCI-1750"]

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
    return Card_PCI1750(datdir)

def editor_name():
    return "Card_PCI1750"