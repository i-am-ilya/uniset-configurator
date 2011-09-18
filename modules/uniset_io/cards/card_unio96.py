# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import base_editor
from global_conf import *

class cid():
  cnum = 0
  cname = 1
  iotype = 2
  subdev = 3

  
class Card_UNIO96():

    def __init__(self,datdir,uifile="card_UNIO96.ui"):

        self.builder = gtk.Builder()
        uifile = datdir+uifile
        self.builder.add_from_file(uifile)
        self.builder.connect_signals(self)

        self.cname = "UNIO86"
        self.clist = self.build_channel_list(self.cname)

        self.node_xmlnode = None
        self.editor_ui = None

        self.module_name = "unioxx5a"
        self.cbox1 = self.builder.get_object("cbox_subdev1")
        self.cbox2 = self.builder.get_object("cbox_subdev2")
        self.cbox3 = self.builder.get_object("cbox_subdev3")
        self.cbox4 = self.builder.get_object("cbox_subdev4")
        self.cbox1.set_active_iter(self.cbox1.get_model().get_iter_first())
        self.cbox2.set_active_iter(self.cbox2.get_model().get_iter_first())
        self.cbox3.set_active_iter(self.cbox3.get_model().get_iter_first())
        self.cbox4.set_active_iter(self.cbox4.get_model().get_iter_first())

        # номера см. исходники модуля unioxx
        #   0 - no use
        #	1 - TBI 24/0
        #	2 - TBI 0/24
        #	3 - TBI 16/8
        self.subdev_type = dict()
        self.subdev_type["0"] = "None"
        self.subdev_type["1"] = "TBI24_0"
        self.subdev_type["2"] = "TBI0_24"
        self.subdev_type["3"] = "TBI16_8"

    def get_supported_cards( self ):
        return ["UNIO96","UNIO48"]

    def check_support( self, cname ):
        if cname.upper() in self.get_supported_cards():
           return True

        return False

    def get_face( self ):
        return self.builder.get_object("main")

    def build_channel_list( self, cname ):
        clist=[]
        for i in range(0,24):
            clist.append([i,"J1:"+str(i),"DI",0])
        for i in range(0,24):
            clist.append([i,"J2:"+str(i),"DI",1])

        if cname == "UNIO48":
           return clist

        for i in range(0,24):
            clist.append([i,"J3:"+str(i),"DI",2])
        for i in range(0,24):
            clist.append([i,"J4:"+str(i),"DI",3])

        return clist

    def init( self, cname, editor_ui, xmlnode ):
        self.editor_ui = editor_ui
        ent_mod_name  = editor_ui.get_object("io_module")
        ent_mod_param  = editor_ui.get_object("io_params")

        ent_mod_name.set_text(self.module_name)
        ent_mod_param.set_text("")
        self.cname = cname
        be = base_editor.BaseEditor(None)
        be.set_combobox_element(self.cbox1,get_str_val(xmlnode.prop("subdev1")))
        be.set_combobox_element(self.cbox2,get_str_val(xmlnode.prop("subdev2")))
        be.set_combobox_element(self.cbox3,get_str_val(xmlnode.prop("subdev3")))
        be.set_combobox_element(self.cbox4,get_str_val(xmlnode.prop("subdev4")))
        
        self.on_unioxx_subdev_changed(self.builder.get_object("cbox_subdev1"))

    def save( self, xmlnode, cname ):
        #xmlnode.setProp("name",self.cname)
        xmlnode.setProp("subdev1",self.cbox1.get_active_text())
        xmlnode.setProp("subdev2",self.cbox2.get_active_text())
        if cname == "UNIO48":
           xmlnode.setProp("subdev3","")
           xmlnode.setProp("subdev4","")
        else:
           xmlnode.setProp("subdev3",self.cbox3.get_active_text())
           xmlnode.setProp("subdev4",self.cbox4.get_active_text())

    def get_channel_list( self, cname ):
        if cname.upper() != self.cname.upper():
           self.clist = self.build_channel_list(cname.upper())

        return self.clist
        
    def get_iotype( self, channel ):
        nchan = to
        for c in self.clist:
            if c[cid.cnum] == channel:
               return c[cid.iotype]

        return "DI"

    def get_typenum_for_unio_subdev(self,sname):
        for k,v in self.subdev_type.items():
            if v == sname:
               return k

        return "0"

    def get_params(self,cardxmlnode):
        s = ""
        maxnum = 5
#        if cardnode.prop("name").upper() == UNIO48:
#            maxnum = 3
        for i in range(1,maxnum):
          p = "subdev" + str(i)
          sname = get_str_val(cardxmlnode.prop(p))
          if s != "":
             s = s + "," + self.get_typenum_for_unio_subdev(sname.upper())
          else:
             s = self.get_typenum_for_unio_subdev(sname.upper())

        return s

    def on_unioxx_subdev_changed(self,cb):
        if self.editor_ui == None:
           return

        s = "%s,%s,%s,%s"%(
           self.get_typenum_for_unio_subdev( self.cbox1.get_active_text() ),
           self.get_typenum_for_unio_subdev( self.cbox2.get_active_text() ),
           self.get_typenum_for_unio_subdev( self.cbox3.get_active_text() ),
           self.get_typenum_for_unio_subdev( self.cbox4.get_active_text() )
        )

        ent_mod_param  = self.editor_ui.get_object("io_params")
        ent_mod_param.set_text(s)

def create_editor(datdir):
    return Card_UNIO96(datdir)

def editor_name():
    return "UNIOxx"