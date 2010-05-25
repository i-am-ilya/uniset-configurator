#!/usr/bin/env python
#-*- coding: utf-8 -*-

from gettext import gettext as _
import gettext
import sys
import gtk
import gobject
import gtk.glade
import maintree
import configure
import libxml2
import UniXML
import locale

locale.setlocale(locale.LC_ALL, "ru_RU.UTF8")

mwinglade="mainwin.glade"
confile="configure.xml"

if len(sys.argv) > 1:
	confile = sys.argv[1]

glade = gtk.glade.XML(mwinglade)

class MainWindow(gtk.Widget):
	def __init__(self):
		glade.signal_autoconnect(self)
		pass

	def on_toolbutton1_clicked(self, button):
		print 'foo!'

	def on_toolbutton2_clicked(self, button):
		print 'foo2!'

	def on_window1_destroy(self, destroy):
		gtk.main_quit()


conf = None                                                                                                                                                                         
try:                                                                                                                                                                                
    conf = configure.Conf(confile,glade)                                                                                                                                             
except:                                                                                                                                                                             
    dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("XML file damage or not found! \n Loading FAILED!"))                                    
    dialog.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray"))                                                                                                                 
    dialog.run()                                                                                                                                                                    
    dialog.destroy()    

tree_swin = glade.get_widget("scwin_left")
mtree = maintree.MainTree(conf)
tree_swin.add(mtree)

MainWindow()
gtk.main()
