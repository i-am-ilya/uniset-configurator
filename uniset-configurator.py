#!/usr/bin/env python
#-*- coding: utf-8 -*-

from gettext import gettext as _
import gettext
import sys
import os
import gtk
import gobject
import gtk.glade
import maintree
import configure
import libxml2
import UniXML
import locale
import dlg_slist

locale.setlocale(locale.LC_ALL, "ru_RU.UTF8")

mwinglade="mainwin.glade"
confile="configure.xml"

if len(sys.argv) > 1:
    confile = sys.argv[1]

glade = gtk.glade.XML(mwinglade)

class MainWindow(gtk.Widget):
    def __init__(self):
        glade.signal_autoconnect(self)
        self.win = glade.get_widget("MainWindow")
        pass

    def on_MainWindow_destroy(self, destroy):
        if conf.is_changed() and conf.xml:
            dlg = gtk.MessageDialog(self.win, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO, _("Save changes?"))
            res = dlg.run()
            if res == gtk.RESPONSE_YES:
               os.rename(conf.xml.getFileName(),str(conf.xml.getFileName())+".bak")
               conf.xml.save()

        gtk.main_quit()

    def on_save_activate(self, data):
        print "on_save_activate: " + str(conf.xml.getFileName())
        if conf.xml:
           os.rename(conf.xml.getFileName(),str(conf.xml.getFileName())+".bak")
           conf.xml.save()
           conf.unmark_changes()

    def on_save_as_activate(self, data):
         print "on_save_as_activate"

conf = None                                                                                                                                                                         
try:                                                                                                                                                                                
    conf = configure.Conf(confile,glade)                                                                                                                                             
except:                                                                                                                                                                             
    dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("XML file damage or not found! \n Loading FAILED!"))                                    
    dialog.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray"))                                                                                                                 
    dialog.run()                                                                                                                                                                    
    dialog.destroy()    

# main tree
tree_swin = glade.get_widget("scwin_left")
mtree = maintree.MainTree(conf)
tree_swin.add(mtree)

#dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO, _("Already exist. \nReconnection?"))
#res = dlg.run()

MainWindow()
gtk.main()
