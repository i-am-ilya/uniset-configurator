# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_editor
from global_conf import *

class fid():
   name = 0
   info = 1
   pic = 2
   etype = 3
   editor = 4

'''
Задачи: настройщик для алгоритма управления свето-звуковой сигнализацией на колонках
'''
class SESEditor(base_editor.BaseEditor, gtk.HBox):

    def __init__(self, conf):

        gtk.HBox.__init__(self)
        base_editor.BaseEditor.__init__(self,conf)

        self.builder = gtk.Builder()
        self.builder.add_from_file(conf.datdir+"seseditor.ui")
        self.builder.connect_signals(self)
  
        self.elements=[
            ["tv","tv_main",None,False],
            ["mod_name","io_module","module",False]
        ]
        self.init_builder_elements(self.elements,self.builder)

        self.tv.reparent(self)

        self.model = None
        self.modelfilter = None
        self.model = gtk.TreeStore(gobject.TYPE_STRING,
                                    gobject.TYPE_STRING,
                                    gtk.gdk.Pixbuf,
                                    gobject.TYPE_STRING,
                                    object)
        
        self.modelfilter = self.model.filter_new()
#       self.modelfilter.set_visible_column(1)

        # create treeview
        self.tv.set_model(self.model)
        self.tv.set_rules_hint(True)
        self.tv.connect("button-press-event", self.on_button_press_event)
    
    def reopen(self):
#        self.model.clear()
#        self.show_all()
        pass

    def on_button_press_event(self, object, event):
#        print "*** on_button_press_event"
        (model, iter) = self.tv.get_selection().get_selected()

        if event.button == 3:
            if not iter:
#                 self.empty_popup.popup(None, None, None, event.button, event.time)
                 return False

#            t = model.get_value(iter,fid.etype)

        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            if not iter:
                 return False

        return False


def create_module(conf):
    return SESEditor(conf)

def module_name():
    return "СЭС"
