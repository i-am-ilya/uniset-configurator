# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import simple_card
from global_conf import *

class Card_KM31LVDT(simple_card.SimpleCard):

    def __init__(self,datdir,uifile="card_KM31LVDT.ui"):

        simple_card.SimpleCard.__init__(self,datdir,uifile)

        self.cname = "KM31LVDT"

        self.params=[
            ["adc0","cb_adc0","pwr_adc0",False],
            ["adc1","cb_adc1","pwr_adc1",False],
            ["adc2","cb_adc2","pwr_adc2",False]
        ]
        self.init_builder_elements(self.params,self.builder)

        self.module_name = "km31lvdt"
        self.default_init(self.cname)

    def get_supported_cards( self ):
        return ["KM31LVDT"]

    def build_channel_list( self, cname ):
        clist=[]
        for i in range(0,16):
            clist.append([i,"(AI)X1:%d"%i,"AI",0])
        for i in range(0,8):
            clist.append([i,"(AI)X3:%d"%i,"AI",1])
        for i in range(0,8):
            clist.append([i,"(AI)X6:%d"%i,"AI",2])

        return clist

    def default_init(self,cname):
        self.adc0.set_active(True)
        self.adc1.set_active(True)
        self.adc2.set_active(True)


    def init( self, cname, editor_ui, xmlnode ):
        self.simple_init(cname,editor_ui,xmlnode)
        self.on_cb_pwr_toggled(self.adc0)

    def save( self, xmlnode, cname ):
        self.simple_save(xmlnode,cname)

    def delete(self,xmlnode,cname):
        xmlnode.setProp("pwr_adc0","")
        xmlnode.setProp("pwr_adc1","")
        xmlnode.setProp("pwr_adc2","")

    def get_params(self,adc0,adc1,adc2):
        pwr = 0

        # см. модль ядра km31LVDT        
        #define PWR_ADC0 0x1
        #define PWR_ADC1 0x2
        #define PWR_ADC2 0x4
#        if adc0:
#           pwr |= 0x1
#        if adc1:
#           pwr |= 0x2
#        if adc2:
#           pwr |= 0x4'''
        return to_str(pwr)

    def get_module_params(self,cnode):
        return self.get_params(
                    cnode.prop("pwr_adc0"),
                    cnode.prop("pwr_adc1"),
                    cnode.prop("pwr_adc2")
                )

    def on_cb_pwr_toggled(self,cb):

        if self.editor_ui == None:
           return

        s = self.get_params(
            to_int(self.adc0.get_active()),
            to_int(self.adc1.get_active()),
            to_int(self.adc2.get_active()),
        )
        ent_mod_param  = self.editor_ui.get_object("io_params")
        ent_mod_param.set_text(s)

    def get_default_channel_param(self,cname):
        ret = dict()
        ret["aref"] = 2
        ret["range"] = 0
        return ret

def create_editor(datdir):
    return Card_KM31LVDT(datdir)

def editor_name():
    return "Card_KM31LVDT"
