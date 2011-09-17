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

    def get_name( self ):
        return module_name()

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

def create_module(datdir):
    return Card_UNIO96(datdir)

def module_name():
    return "UNIO96"
