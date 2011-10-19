# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_editor
from global_conf import *
import dlg_xlist
from LinkEditor import *

class GEUPanel(base_editor.BaseEditor):

    def __init__(self, conf):

        base_editor.BaseEditor.__init__(self,conf)

        self.builder = gtk.Builder()
        self.builder.add_from_file(conf.datdir+"geu_panel.ui")
        self.builder.connect_signals(self)

        self.elements=[
            ["win","main_window",None,False],
            ["ctl_box","ctl_box",None,False],
            ["win_aps","win_aps",None,False],
            ["entName","entName",None,False]
        ]
        self.init_builder_elements(self.elements,self.builder)

        self.editor = LinkEditor(conf,conf.datdir+"geu.cpanel.src.xml")
        face = self.editor.get_face()
        face.reparent(self.ctl_box)

        import apspanel
        self.apspanel = apspanel.APSPanelEditor(conf)
        self.win_aps.add(self.apspanel)
        self.apspanel.show_all()

    def run(self, xmlnode):

        self.editor.pre_init(xmlnode)
        self.init_apspanel(xmlnode)
        res = self.win.run()
        self.win.hide()
        if res != dlg_RESPONSE_OK:
           return False

        self.editor.save(xmlnode)
        xmlnode.setProp("name", self.entName.get_text())
        return True

    def init_apspanel(self, xmlnode):
        self.apspanel.clear()
        if not xmlnode:
           return

        self.entName.set_text( to_str(xmlnode.prop("name")) )
        node = self.conf.xml.findNode(xmlnode,"APSPanel")[0]
        if node:
           self.apspanel.init(node)
