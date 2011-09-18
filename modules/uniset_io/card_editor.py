# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import base_editor
from global_conf import *

class CardEditor(base_editor.BaseEditor):

    def __init__(self,conf,ioconf,datdir,uifile="editor.ui"):

        base_editor.BaseEditor.__init__(self,conf)

        self.ioconf = ioconf

        self.builder = gtk.Builder()
        self.builder.add_from_file(datdir+uifile)
        self.builder.connect_signals(self)

        # Список параметров для карты
        self.card_params=[
            ["dlg_card","dlg_card","name",False],
            ["cardmain","cardmain",None,True],
            ["cardlist","io_cardlist","name",False],
            ["card_number","io_sp_cardnum","card",False],
            ["card_ba","io_baddr","baddr",False],
            ["iodev","io_dev","dev",False],
            ["mod_params","io_params","module_params",False],
            ["mod_name","io_module","module",False]
        ]
        self.init_builder_elements(self.card_params,self.builder)
        
        cmodel = gtk.ListStore(str, object)
        self.cardlist.set_model(cmodel)
        for k, v in self.ioconf.editors.items():
            #self.cardmain.add(v.get_face())
            v.get_face().reparent(self.cardmain)
            v.get_face().hide()
            for c in v.get_supported_cards():
                cmodel.append([c,v])

        self.cnode = None

    def card_name(self):
        return self.cardlist.get_active_text()

    def ba(self):
        return self.card_ba.get_text()

    def card_num(self):
        return self.card_number.get_value_as_int()

    def default_init(self):
        self.card_ba.set_text("")
        self.card_number.set_value(0)
        self.mod_params.set_text("")
        self.mod_name.set_text("")
        self.set_combobox_element(self.cardlist,"None")

    def run(self, cnode=None):
        self.cnode = cnode
        if cnode:
           # при редактировании отключаем выбор, т.к.
           # сменить тип карты можно только удалив старую
           # (со всеми привязками и т.п)
           self.cardlist.set_sensitive(False)
           self.init_elements_value(self.card_params,cnode)
        else:
           self.cardlist.set_sensitive(True)
           self.default_init()

        e_it = self.cardlist.get_active_iter()
        if e_it:
           editor = self.cardlist.get_model().get_value(e_it,1)
           editor.init(self.cardlist.get_active_text(),self.builder,cnode)

        if self.iodev.get_text() == "":
           self.iodev.set_text("/dev/comedi%d"%self.card_number.get_value_as_int())

        self.on_io_cardlist_changed(self.cardlist)
        ret = self.dlg_card.run()
        self.dlg_card.hide()
        if self.cardlist.get_active_text() == "None":
           ret = 0
        self.cardlist.set_sensitive(True)
        return ret

    def save(self,cnode):

        if not cnode:
           return

        c_it = self.cardlist.get_active_iter()
        if c_it:
           editor = self.cardlist.get_model().get_value(c_it,1)
           editor.save(cnode,self.cardlist.get_active_text())

        self.save2xml_elements_value(self.card_params,cnode)

    def on_io_cardlist_changed(self,cb):

        #if not self.cnode:
        #   return

        cname = cb.get_active_text()
        editor = cb.get_model().get_value(cb.get_active_iter(),1)
        face = editor.get_face()
        face.reparent(self.cardmain)
        editor.init(cname,self.builder,self.cnode)

        it = cb.get_model().get_iter_first()
        while it is not None:
            e = cb.get_model().get_value(it,1)
            if e.check_support(cname):
               e.get_face().show()
            else:
               e.get_face().hide()

            it = cb.get_model().iter_next(it)

    def io_sp_cardnum_value_changed_cb(self,sp):
        self.iodev.set_text("/dev/comedi%d"%self.card_number.get_value_as_int())
