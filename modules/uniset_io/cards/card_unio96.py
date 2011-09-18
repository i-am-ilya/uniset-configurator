# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML

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

        self.clist = self.build_channel_list()

        self.node_xmlnode = None
        self.editor_ui = None

        self.module_name = "unioxx5a"
        cbox1 = self.builder.get_object("cbox_subdev1")
        cbox2 = self.builder.get_object("cbox_subdev2")
        cbox3 = self.builder.get_object("cbox_subdev3")
        cbox4 = self.builder.get_object("cbox_subdev4")
        cbox1.set_active_iter(cbox1.get_model().get_iter_first())
        cbox2.set_active_iter(cbox2.get_model().get_iter_first())
        cbox3.set_active_iter(cbox3.get_model().get_iter_first())
        cbox4.set_active_iter(cbox4.get_model().get_iter_first())

    def get_supported_cards( self ):
        return ["UNIO96","UNIO48"]

    def check_support( self, cname ):
        if cname.upper() in self.get_supported_cards():
           return True

        return False

    def get_face( self ):
        return self.builder.get_object("main")

    def build_channel_list( self ):
        clist=[]
        for i in range(0,24):
            clist.append([i,"J1:"+str(i),"DI",0])
        for i in range(0,24):
            clist.append([i,"J2:"+str(i),"DI",1])
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
    
    def get_channel_list( self ):
        return self.clist
        
    def get_iotype( self, channel ):
        nchan = to
        for c in self.clist:
            if c[cid.cnum] == channel:
               return c[cid.iotype]

        return "DI"

    def get_typenum_for_unio_subdev(self,sname):
        # номера см. исходники модуля unioxx
        #   0 - no use
        #	1 - TBI 24/0
        #	2 - TBI 0/24
        #	3 - TBI 16/8
        if sname == "TBI24_0":
           return "1"
        if sname == "TBI0_24":
           return "2"
        if sname == "TBI16_8":
           return "3"
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
        cbox1 = self.builder.get_object("cbox_subdev1")
        cbox2 = self.builder.get_object("cbox_subdev2")
        cbox3 = self.builder.get_object("cbox_subdev3")
        cbox4 = self.builder.get_object("cbox_subdev4")

        s = "%s,%s,%s,%s"%(
           self.get_typenum_for_unio_subdev( cbox1.get_model().get_value(cbox1.get_active_iter(),0) ),
           self.get_typenum_for_unio_subdev( cbox2.get_model().get_value(cbox2.get_active_iter(),0) ),
           self.get_typenum_for_unio_subdev( cbox3.get_model().get_value(cbox3.get_active_iter(),0) ),
           self.get_typenum_for_unio_subdev( cbox4.get_model().get_value(cbox4.get_active_iter(),0) )
        )

        ent_mod_param  = self.editor_ui.get_object("io_params")
        ent_mod_param.set_text(s)

def create_editor(datdir):
    return Card_UNIO96(datdir)

def editor_name():
    return "UNIOxx"