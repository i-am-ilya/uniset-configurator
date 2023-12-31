# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import simple_card
from global_conf import *

class Card_UNIO96(simple_card.SimpleCard):

    def __init__(self,datdir,uifile="card_UNIO96.ui"):

        simple_card.SimpleCard.__init__(self,datdir,uifile)

        self.cname = "UNIO96"

        self.params=[
            ["cbox1","cbox_subdev1","subdev1",False],
            ["cbox2","cbox_subdev2","subdev2",False],
            ["cbox3","cbox_subdev3","subdev3",False],
            ["cbox4","cbox_subdev4","subdev4",False],
        ]
        self.init_builder_elements(self.params,self.builder)

        self.module_name = "unioxx5"
        self.default_init(self.cname)

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
        return ["UNIO96","UNIO48","UNIO96-1"]

    def build_channel_list( self, cname ):
        clist=[]
        for i in range(0,24):
            clist.append([i,"J1:"+str(i),"",0])
        for i in range(0,24):
            clist.append([i,"J2:"+str(i),"",1])

        if cname == "UNIO48":
           return clist

        for i in range(0,24):
            clist.append([i,"J3:"+str(i),"",2])
        for i in range(0,24):
            clist.append([i,"J4:"+str(i),"",3])

        return clist

    def default_init(self,cname):
        self.cbox1.set_active(0)
        self.cbox2.set_active(0)
        self.cbox3.set_active(0)
        self.cbox4.set_active(0)

    def init( self, cname, editor_ui, xmlnode ):
 
        self.simple_init(cname,editor_ui,xmlnode)

        # имтитируем изменения, чтобы обновилась запись в mod_param
        self.on_unioxx_subdev_changed(self.cbox1)

        self.cbox1.set_sensitive(True)
        self.cbox2.set_sensitive(True)
        if cname == "UNIO48":
           self.cbox3.set_active(0)
           self.cbox4.set_active(0)
           self.cbox3.set_sensitive(False)
           self.cbox4.set_sensitive(False)
        else:
           self.cbox3.set_sensitive(True)
           self.cbox4.set_sensitive(True)

    def save( self, xmlnode, cname ):
        self.simple_save(xmlnode,cname)
        if cname == "UNIO48":
           xmlnode.setProp("subdev3","")
           xmlnode.setProp("subdev4","")

    def delete(self,xmlnode,cname):
        xmlnode.setProp("subdev1","")
        xmlnode.setProp("subdev2","")
        xmlnode.setProp("subdev3","")
        xmlnode.setProp("subdev4","")

    def get_typenum_for_unio_subdev(self,sname):
        for k,v in self.subdev_type.items():
            if v == sname:
               return k

        return "0"

    def get_module_params(self,cnode):
        s = ""
        maxnum = 5
#        if cardnode.prop("name").upper() == UNIO48:
#            maxnum = 3
        for i in range(1,maxnum):
          p = "subdev" + str(i)
          sname = to_str(cnode.prop(p))
          if s != "":
             s = s + "," + self.get_typenum_for_unio_subdev(sname.upper())
          else:
             s = self.get_typenum_for_unio_subdev(sname.upper())

        return s
	
    def get_subdev_name(self,subdev):
        sn = to_str(subdev)
        if sn == "0":
           return self.cbox1.get_active_text()
        if sn == "1":
           return self.cbox2.get_active_text()
        if sn == "2":
           return self.cbox3.get_active_text()
        if sn == "3":
           return self.cbox4.get_active_text()

        return ""
	
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
        
    def get_iotype( self, cname, subdev, channel ):
        clist = self.get_channel_list(cname)
        subdev = to_str(subdev)
        subnum = to_int(subdev)
        channel = to_int(channel)

        for c in clist:
            if c[simple_card.cid.cnum] == channel and c[simple_card.cid.subdev] == subnum:
            
               subdev_name = self.get_subdev_name(subdev)
               if subdev_name == "TBI0_24":
                  return "DO"
               if subdev_name == "TBI24_0":
                  return "DI"
               if subdev_name == "TBI16_8":
                  if channel > 15:
                     return "DO"
                  return "DI"

        return ""

def create_editor(datdir):
    return Card_UNIO96(datdir)

def editor_name():
    return "UNIOxx"