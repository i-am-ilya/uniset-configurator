#!/usr/bin/env python
#-*- coding: utf-8 -*-

from gettext import gettext as _
import gettext
import sys
import os
import gtk
import gobject
import gtk.glade
import configure
import libxml2
import UniXML
import locale

# modules
import io_main
import can_main



locale.setlocale(locale.LC_ALL, "ru_RU.UTF8")

mwinglade="mainwin.glade"
glade = gtk.glade.XML(mwinglade)
conf = None                                                                                                                                                                         

class MainWindow(gtk.Widget):
    def __init__(self):
        glade.signal_autoconnect(self)
        self.win = glade.get_widget("MainWindow")

    def on_MainWindow_destroy(self, destroy):
        self.check_changes()
        gtk.main_quit()

    def on_save_activate(self, data):
        print "on_save_activate: " + str(conf.xml.getFileName())
        if conf.xml:
           os.rename(conf.xml.getFileName(),str(conf.xml.getFileName())+".bak")
           conf.xml.save()
           conf.unmark_changes()

    def on_save_as_activate(self, data):
         print "on_save_as_activate"

    def on_open_activate(self, data):
        self.check_changes()

        dlg = gtk.FileChooserDialog(_("File selection"),action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        res = dlg.run()
        dlg.hide()
        if res == gtk.RESPONSE_OK:
            confile = dlg.get_filename()
            conf.reopen(confile)

    def on_quit_activate(self, data):
        self.check_changes()
        gtk.main_quit()

    def check_changes(self):
        if conf.is_changed() and conf.xml:
            dlg = gtk.MessageDialog(self.win, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO, _("Save changes?"))
            res = dlg.run()
            if res == gtk.RESPONSE_YES:
               os.rename(conf.xml.getFileName(),str(conf.xml.getFileName())+".bak")
               conf.xml.save()
            conf.unmark_changes()


#def main():

# for debug
confile="configure.xml"
#confile=""

if len(sys.argv) > 1:
   confile = sys.argv[1]

if confile == "":
   dlg = gtk.FileChooserDialog(_("File selection"),action=gtk.FILE_CHOOSER_ACTION_OPEN,
   buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
   res = dlg.run()
   dlg.hide()
   if res == gtk.RESPONSE_OK:
       confile = dlg.get_filename()

try:
   conf = configure.Conf(confile,glade) 
except: 
   dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("XML file damage or not found! \n Loading FAILED!"))
   dialog.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray")) 
   dialog.run()
   dialog.destroy()


def add_module( face, lbl, mainbook, glade ):
    # main tree
    scwin = gtk.ScrolledWindow()
    scwin.show()
    scwin.add(face)
    face.show()
    l = gtk.Label(lbl)
    l.show()
    mainbook.append_page(scwin,l)


mainbook = glade.get_widget("mainbook")

# I/O configure
io_mtree = io_main.IOMain(conf)
add_module(io_mtree,"I/O",mainbook,glade)

# CAN configure
can_mtree = can_main.CANMain(conf)
add_module(can_mtree,"CAN",mainbook,glade)

# ---------------
mainbook.show()
MainWindow()
gtk.main()
