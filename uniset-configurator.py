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
import io_editor
import can_editor
import nodes_editor
import uniset_editor
import lcaps_editor



locale.setlocale(locale.LC_ALL, "ru_RU.UTF8")
#loc = findarg("--localepath=", "./locale")
#locale.setlocale(locale.LC_ALL,'')
#gettext.bindtextdomain("uniset-configurator", loc)
#gettext.textdomain("uniset-configurator")

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


conf = None                                                                                                                                                                         

is_system_run_flag = sys.argv[0].startswith("./")
datdir = ( "/usr/share/uniset-configurator/" if not is_system_run_flag else "./" )
mwinglade = datdir + "mainwin.glade"

# for debug
#confile="configure.xml"
confile=""

try:
    glade = gtk.glade.XML(mwinglade)
except: 
   dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("Glade file damage or not found! \n Loading FAILED!"))
   dialog.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray")) 
   dialog.run()
   dialog.destroy()

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
   conf = configure.Conf(confile,glade,datdir) 
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
    scwin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
    face.show()
    l = gtk.Label(lbl)
    l.show()
    mainbook.append_page(scwin,l)

mainbook = glade.get_widget("mainbook")
# -------------------
"""
 Создавать обязательно перед всеми
 т.к. многие модули могут "хотеть" подключится
 к сигналам
"""
# Nodes configure
nodes_mtree = nodes_editor.NodesEditor(conf)
add_module(nodes_mtree,"Nodes",mainbook,glade)
# -------------------
# I/O configure
io_mtree = io_editor.IOEditor(conf)
add_module(io_mtree,"I/O",mainbook,glade)

# CAN configure
can_mtree = can_editor.CANEditor(conf)
add_module(can_mtree,"CAN",mainbook,glade)

# UniSet configure
uniset_w = uniset_editor.UniSetEditor(conf)
add_module(uniset_w,"UniSet",mainbook,glade)

# LCAPS editor
lcaps_mtree = lcaps_editor.LCAPSEditor(conf)
add_module(lcaps_mtree,"LCAPS",mainbook,glade)

# ---------------
mainbook.show()
MainWindow()
gtk.main()
