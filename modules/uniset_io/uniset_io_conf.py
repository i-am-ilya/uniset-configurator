#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import sys
is_system_run_flag = sys.argv[0].startswith("./")
if is_system_run_flag:
   sys.path.append("../../")

from gettext import gettext as _
import re
import datetime
import UniXML
import os
from global_conf import *

'''
Класс реализующий всё что касается работы с настройками в/в (comedi):
1. Типы карт, параметры, модули ядра и т.п.
2. Он же консольный генератор скрипта настройки ctl-comedi.sx

Здесь используется подход, как с "плагинами". В каталоге 'cards/'
лежат редакторы для разных карт, которые реализуют "одинаковый" интерфейс.
Все редакторы задаются шаблонным именем 'card_XXX.py'.
При старте системы, все они считываются и формируется список доступных карт.

Для добавления нового типа карты, достаточно поместить редактор в каталог 'cards/',
сделав его по подобию других. Базовым классом для редакторов является 'simple_card.py'.
'''
class IOConfig():

    def __init__(self,xml,datdir):
        self.xml = xml
        self.datdir = datdir
        self.templdir = self.datdir + "templates/io/"
        self.moddir = self.datdir + "cards/"
        self.cardlist = dict()
        self.editors = dict()
        self.load_card_editors()
    
    def load_card_editors(self):
        #modlist=[]
        sys.path.append(self.moddir[:-1])
        for name in os.listdir(self.moddir):
            if name.startswith('card_') == False or name.endswith('.py') == False:
               continue

            m = __import__(name[:-3],globals())
            editor = m.create_editor(self.moddir)
            self.editors[m] = editor
            for cname in editor.get_supported_cards():
                self.cardlist[cname.upper()] = editor

    def get_channel_list(self, cardnode):
        cname = cardnode.prop("name").upper()
        if cname in self.cardlist:
           editor = self.cardlist[cname]
           return editor.get_channel_list(cname)

        return [[0,"Unknown CARD","",0]]

    def get_iotype(self,cname,subdev,channel):
        cname = cname.upper()
        if cname in self.cardlist:
           editor = self.cardlist[cname]
           return editor.get_iotype(cname,subdev,channel)

        return ""
   
    def get_default_channel_param(self,cname):
        cname = cname.upper()
        if cname in self.cardlist:
           editor = self.cardlist[cname]
           return editor.get_default_channel_param(cname)

        ret = dict()
        return ret
    
    def get_module_params_for_card(self,cardnode):
        cname = cardnode.prop("name").upper()
        if cname in self.cardlist:
           editor = self.cardlist[cname]
           return [editor.get_module_name(),editor.get_module_params(cardnode,cname)]
        
        return ["",""]

    def gen_comedi_script(self,xmlnode,fname):
         cardsinfo = [] # [module,params,dev,baddr]
         modlist = {} # делаем словарь, чтобы исключить повторяющиеся модули..
         modlist_ignore = {}
         modlist_all = {}

         while xmlnode != None:
            
#            if to_str(xmlnode.prop("ignore")) != "":
#               xmlnode = self.xml.nextNode(xmlnode)
#               continue         
            
            mod_name = to_str(xmlnode.prop("module"))
            mod_params = to_str(xmlnode.prop("module_params"))
            IGN = to_str(xmlnode.prop("ignore"))
            if mod_name != "":
               modlist_all[mod_name] = mod_name
               if IGN == "":
                  modlist[mod_name] = mod_name
               
            cardsinfo.append( [mod_name,mod_params,to_str(xmlnode.prop("dev")),to_str(xmlnode.prop("baddr")),IGN] )
            xmlnode = self.xml.nextNode(xmlnode)

         for m in modlist_all:
             if m not in modlist:
                modlist_ignore[m] = m
         
         gdate = datetime.datetime.today()
         ctx = open( self.templdir + "ctl-comedi-skel.sh" ).readlines()
         out = open(fname,"w")
         for l in ctx:
             if re.search("{MOD_PROBE}",l):
                l = self.gen_modprobe_string(modlist,modlist_ignore,l)
             
             if re.search("{MOD_REMOVE}",l):
                l = self.gen_rmmod_string(modlist,modlist_ignore,l)
             
             if re.search("{CARDS_CONFIG}",l):
                l = self.gen_cardsconf_string(cardsinfo,l)
             
             if re.search("{CARDS_REMOVE}",l):
                l = self.gen_rmcards_string(cardsinfo,l)
             
             if re.search("{GENDATE}",l):
                l = re.sub("{GENDATE}",gdate.ctime(),l)
             
             out.write(l)
         
         out.close()
    
    def gen_modprobe_string(self,modlist,modlist_ignore,l):
        s = ""
        for m in modlist:
            s += re.sub("{MOD_PROBE}", str("modprobe " + m),l)
        for m in modlist_ignore:
            s += re.sub("{MOD_PROBE}", str("# modprobe " + m),l)

        return s
    
    def gen_rmmod_string(self,modlist,modlist_ignore,l):
        s = ""
        for m in modlist:
            s += re.sub("{MOD_REMOVE}", str("rmmod " + m),l)
        for m in modlist_ignore:
            s += re.sub("{MOD_REMOVE}", str("# modprobe " + m),l)

        return s
    
    def gen_rmcards_string(self,cardsinfo,l):
        s = ""
        for m in cardsinfo:
            dev = m[2]
            if dev == "":
               dev = "/dev/comedi???"

            IGN=""
            if m[4]!="": IGN="#"

            s += re.sub("{CARDS_REMOVE}", str(IGN+"/usr/sbin/comedi_config -r " + dev + " || RETVAL=1"),l)
        return s

#  /usr/sbin/comedi_config /dev/comedi0 di32_5 0x100 || RETVAL=1
    def gen_cardsconf_string(self,cardsinfo,l):
        s = ""
        for m in cardsinfo:
            mod = m[0]
            if mod == "":
               mod = "??module??"
            ba = m[3]
            if ba == "":
               ba = "??BaseAdress??"
            dev = m[2]
            if dev == "":
               dev = "/dev/comedi???"
            params = m[1]
            if params != "":
               params = "," + params

            IGN=""
            if m[4]!="": IGN="#"
            
            s += re.sub("{CARDS_CONFIG}", str(IGN+"/usr/sbin/comedi_config " + dev + " " + mod + " " + ba + params + " || RETVAL=1"),l)
        return s

    def get_outfilename(self, xmlnode):
        nname = xmlnode.prop("ip").lower()
        # некорректная проверка на то, что это IP
        # надо потом переделать на регулярное выражение
        if nname.find(".") != -1:
            nname = xmlnode.prop("name").lower()
        return "ctl-comedi-" + nname + ".sh"

if __name__ == "__main__":

    from uniset_io_conf import *
    from cmd_param import *

    is_system_run_flag = sys.argv[0].startswith("./")
    datdir = ( "/usr/share/uniset-configurator/" if not is_system_run_flag else "./" )
    templdir=( datdir + "templates/io/" if not is_system_run_flag else "./templates/" )

    confile = ""
    if checkArgParam("--help",False) == True or checkArgParam("-h",False) == True:
       print "Usage: %s [--confile configure.xml ] [--outfile filename]  --gen-comedi-conf Nodename" % sys.argv[0]
       print "--confile confile           - Configuration file. Default: configure.xml"
       print "--gen-comedi-conf nodename  - Generate ctl-comedi-xxx.sh for nodename."
       print "--outfile filename          - Save to filename. Default: ctl-comedi-'nodename'.sh"
       print "-v                          - Verbose mode"
       exit(0)

    confile = getArgParam("--confile","configure.xml")
    nodename = getArgParam("--gen-comedi-conf","")
    verb = checkArgParam("-v",False)
    
    if nodename == "":
       print "Usage: %s [--confile configure.xml ] [--outfile filename]  --gen-comedi-conf Nodename" % sys.argv[0]
       exit(1)
    
    outfile = getArgParam("--outfile","")
    
    xml = UniXML.UniXML(confile)
    
    xmlnode = xml.findNode(xml.getDoc(),"nodes")[0].children.next
    xmlnode = xml.getNode(xmlnode)
    while xmlnode != None:
       if xmlnode.prop("name") == nodename:
          break;
       xmlnode = xml.nextNode(xmlnode)
    
    if xmlnode == None:
       print "%s not found in <nodes> (confile: %s)" % (nodename,confile)
       exit(1)
    
    cardnode = xml.findNode(xmlnode,"iocards")[0].children.next
    cardnode = xml.getNode(cardnode)
    if cardnode == None:
       print "<iocards> not found for node='%s' (confile: %s)" % (nodename,confile)
       exit(1)

    ioconf = IOConfig(xml,datdir)

    if outfile == "":
       outfile = ioconf.get_outfilename(xmlnode)

    ioconf.gen_comedi_script(cardnode,outfile)
    if verb == True:
       print "Generate %s OK." % outfile
    
    exit(0)
