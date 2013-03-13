# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import simple_card
from global_conf import *

class Card_None(simple_card.SimpleCard):

    def __init__(self,datdir,uifile="card_None.ui"):

        simple_card.SimpleCard.__init__(self,datdir,uifile)

        self.cname = "None"
        self.node_xmlnode = None
        self.editor_ui = None
        self.module_name = ""

    def get_supported_cards( self ):
        return ["None"]

    def init( self, cname, editor_ui, xmlnode ):
        self.simple_init(cname,editor_ui,xmlnode)

    def save( self, xmlnode, cname ):
        self.simple_save(xmlnode,cname)

def create_editor(datdir):
    return Card_None(datdir)

def editor_name():
    return "None"