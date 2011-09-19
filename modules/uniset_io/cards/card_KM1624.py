# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import simple_card
from global_conf import *

class Card_KM1624(simple_card.SimpleCard):

    def __init__(self,datdir,uifile="card_KM1624.ui"):

        simple_card.SimpleCard.__init__(self,datdir,uifile)

        self.cname = "KM1624"
        self.clist = self.build_channel_list(self.cname)

        self.params=[
            ["adc","cb_adc","pwr_adc",False],
            ["dac0","cb_dac0","pwr_dac0",False],
            ["dac1","cb_dac1","pwr_dac1",False],
            ["dac2","cb_dac2","pwr_dac2",False],
            ["dac3","cb_dac3","pwr_dac3",False]
        ]
        self.init_builder_elements(self.params,self.builder)

        self.module_name = "km1624"
        self.default_init(self.cname)

    def get_supported_cards( self ):
        return ["KM1624"]

    def build_channel_list( self, cname ):
        clist=[]
        for i in range(0,16):
            clist.append([i,"AI:"+str(i),"AI",0])
        for i in range(0,4):
            clist.append([i,"AO:"+str(i),"AO",1])

        return clist

    def default_init(self,cname):
        self.adc.set_active(True)
        self.dac0.set_active(True)
        self.dac1.set_active(True)
        self.dac2.set_active(True)
        self.dac3.set_active(True)

    def init( self, cname, editor_ui, xmlnode ):
        self.simple_init(cname,editor_ui,xmlnode)
        self.on_cb_pwr_toggled(self.adc)

    def save( self, xmlnode, cname ):
        self.simple_save(xmlnode,cname)

    def get_params(self,adc,dac0,dac1,dac2,dac3):
        pwr = 0
        # см. модль ядра km1624        
        #define PWR_ADC 0x1
        #define PWR_DAC0 0x2
        #define PWR_DAC1 0x4
        #define PWR_DAC2 0x8
        #define PWR_DAC3 0x10
        if adc:
           pwr |= 0x1
        if dac0:
           pwr |= 0x2
        if dac1:
           pwr |= 0x4
        if dac2:
           pwr |= 0x8
        if dac3:
           pwr |= 0x10

        return to_str(pwr)

    def get_module_params(self,cnode):
        return self.get_params(
                    cnode.prop("pwr_adc"),
                    cnode.prop("pwr_dac0"),
                    cnode.prop("pwr_dac1"),
                    cnode.prop("pwr_dac2"),
                    cnode.prop("pwr_dac3")
                )

    def on_cb_pwr_toggled(self,cb):

        if self.editor_ui == None:
           return

        s = self.get_params(
            to_int(self.adc.get_active()),
            to_int(self.dac0.get_active()),
            to_int(self.dac1.get_active()),
            to_int(self.dac2.get_active()),
            to_int(self.dac3.get_active())
        )
        ent_mod_param  = self.editor_ui.get_object("io_params")
        ent_mod_param.set_text(s)

    def get_default_channel_param(self,cname):
        ret = dict()
        ret["aref"] = 2
        ret["range"] = 0
        return ret

def create_editor(datdir):
    return Card_KM1624(datdir)

def editor_name():
    return "Card_KM1624"