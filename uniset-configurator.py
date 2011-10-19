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
from global_conf import *
import LinkEditor


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
           #os.rename(conf.xml.getFileName(),str(conf.xml.getFileName())+".bak")
           conf.xml.save(None,True,True)
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
               #os.rename(conf.xml.getFileName(),str(conf.xml.getFileName())+".bak")
               conf.xml.save(None,True,True)
            conf.unmark_changes()


conf = None                                                                                                                                                                         

moddir = ".modules"
for p in sys.path:
    if  os.path.basename(p) == "uniset-configurator":
        moddir = p + "/modules"
        break

is_system_run_flag = sys.argv[0].startswith("./")
datdir = ( "/usr/share/uniset-configurator/" if not is_system_run_flag else "./" )
#moddir = ( "/usr/share/uniset-configurator/"+modules if not is_system_run_flag else "./modules" )

sys.path.append(datdir)
sys.path.append(moddir)

if is_system_run_flag:
   sys.path.append("./")

mwinglade = datdir + "mainwin.glade"

# for debug
#confile="configure.xml"
confile=""

rewrite_confile = False

try:
    glade = gtk.glade.XML(mwinglade)
except: 
   dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("Glade file damage or not found! \n Loading FAILED!"))
   dialog.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray")) 
   dialog.run()
   dialog.destroy()

if len(sys.argv) > 1:
   confile = getArgParam("--confile",sys.argv[1])
   rewrite_confile = checkArgParam("--rewrite",False)
   if rewrite_confile == True:
      if confile == "":
         print "Unknown confile. Use --confile filename\n"
         exit(1)

      rewrite_filename = getArgParam("--rewrite",confile)
      try:
           xml = UniXML.UniXML(confile)
      except:
           print "Can`t open XML file '%s'\n"%confile
           exit(1)

      backup = False
      if rewrite_filename == confile:
         backup = True

      xml.save(rewrite_filename,True,backup)
      exit(0)

if confile == "":
   dlg = gtk.FileChooserDialog(_("File selection"),action=gtk.FILE_CHOOSER_ACTION_OPEN,
   buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
   res = dlg.run()
   dlg.hide()
   if res != gtk.RESPONSE_OK:
      exit(0)
   
   confile = dlg.get_filename()

try:
   conf = configure.Conf(confile,glade,datdir,moddir) 
except: 
   dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, _("XML file damage or not found! \n Loading FAILED!"))
   dialog.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray")) 
   dialog.run()
   dialog.destroy()
   exit(1)

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
    conf.add_module(face)

mainbook = glade.get_widget("mainbook")
# -------------------
# load modules
modlist=[]
imodules = dict()
for name in os.listdir(moddir):
    fullname = os.path.join(moddir, name)
    if os.path.isdir(fullname):
        sys.path.append(fullname)
        modlist.append(name)
        mlist = map(__import__,[name])
        for i in mlist:
            imodules[name] = i

# read priority list

prior_mlist = []
if os.path.exists(moddir+"/priority.list"):
   mlist = open(moddir+"/priority.list").readlines()
   for n in mlist:
       n = n.strip()
       if imodules.has_key(n):
          prior_mlist.append(n)

load_list = prior_mlist

# добавляем оставшиеся найденные, но которых нет в списке загрузки
for n in modlist:
    if n not in prior_mlist:
       if imodules.has_key(n):
          load_list.append(n)

if len(sys.argv) > 1:
   ind = findArgParam("--linkedit")
   if ind != -1:
      if len(sys.argv) < ind+2:
         print "Unknown confname or object. Use --linkedit confname source.xml\n"
         exit(1)

      cname = sys.argv[ind+1]
      src_file = sys.argv[ind+2]

      xmlnode = conf.xml.findNode(conf.xml.getDoc(),cname)[0]
      if xmlnode == None:
         print "%s not found\n"%oname
         exit(1)

      mwin = glade.get_widget("MainWindow")
      #mwin.set_visible(False)
      #mwin.resize(1,1)
#      mwin.set_decorated(False)
#      mwin.set_default_size(10,10)
      mwin.hide()
      ed = LinkEditor.create_module(conf)
      ed.build_editor(src_file)
      if ed.run(xmlnode) and conf.is_changed():
         conf.xml.save(None,True,True)

      exit(0)

# загружаем согласно списку
for n in load_list:
    m = imodules[n]
    face = m.create_module(conf)
    add_module(face,m.module_name(),mainbook,glade)
# ---------------
mainbook.show()
MainWindow()
gtk.main()
