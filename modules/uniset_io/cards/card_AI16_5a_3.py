# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import card_AIxx5a
from global_conf import *

class Card_AI16_5a_3(card_AIxx5a.Card_AIxx5a):

    def __init__(self,datdir,uifile="card_AIxx5a.ui"):

        card_AIxx5a.Card_AIxx5a.__init__(self,datdir,uifile)
        self.cname = "AI16-5a-3"

    def get_supported_cards( self ):
        return ["AI16-5A-3"]

def create_editor(datdir):
    return Card_AI16_5a_3(datdir)

def editor_name():
    return "Card_AI16_5a_3"