# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_editor
from global_conf import *

class SESPanel(base_editor.BaseEditor):

    def __init__(self, conf):

        base_editor.BaseEditor.__init__(self,conf)

        self.builder = gtk.Builder()
        self.builder.add_from_file(conf.datdir+"ses_panel.ui")
        self.builder.connect_signals(self)
  
        self.elements=[
            ["win","main_window",None,False],
            ["name","name",None,False],
            ["loclmp","entLocalLamp","lmpCtlLocal_c",True],
            ["locbtn","btnLocalLamp",None,False],
            ["pultlmp","entPultLamp","lmpCtlPult_c",True],
            ["pultbtn","btnPultLamp",None,False],
            ["autolmp","entAutoLamp","lmpCtlAuto_c",True],
            ["autobtn","btnAutoLamp",None,False],
            ["qgONlmp","entQG_ONlmp","lmpQG_ON_c",True],
            ["qgONbtn","btnQG_ONlmp",None,False],
            ["qgOFFlmp","entQG_OFFlmp","lmpQG_OFF_c",True],
            ["qgOFFbtn","btnQG_OFFlmp",None,False]
        ]
        self.init_builder_elements(self.elements,self.builder)

    def init_panel(self, xmlnode):
        pass