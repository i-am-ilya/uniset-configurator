#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
is_system_run_flag = sys.argv[0].startswith("./")
if is_system_run_flag:
   sys.path.append("../../")

from gettext import gettext as _
import re
import datetime
import UniXML
from global_conf import *

'''
Класс реализующий всё что касается работы с настройками CAN
1. Типы карт, параметры, модули ядра и т.п.
2. Он же консольный генератор скрипта настройки ctl-can.sh
'''
class CANConfig():

    def __init__(self,xml,datdir):
        self.xml = xml
        self.datdir = datdir
        
        # словарь поддерживаемых карт
        # к сожалению заполняется пока вручную
        self.cards = dict()
        
        c1 = dict()
        c1["name"] = "cpc108"
        c1["module"] = "fastwel_cancpc108"
        c1["textname"] = "Fastwel CPC108"
        self.add_card(c1)

        c2 = dict()
        c2["name"] = "pci1680"
        c2["module"] = "pci1680"
        c2["textname"] = "Advantech PCI1680"
        self.add_card(c2)
        
        c3 = dict()
        c3["name"] = "can200mp"
        c3["module"] = "can200"
        c3["textname"] = "Элкус CAN200MP"
        self.add_card(c3)
    
    def add_card(self,c):
        self.cards[c["name"]] = c

    def gen_conf_script(self,xmlnode,fname):
         
         modlist = [] # делаем словарь, чтобы исключить повторяющиеся модули..
         while xmlnode != None:
            mod_name = to_str(xmlnode.prop("module"))
            mod_params = to_str(xmlnode.prop("module_param"))
            modlist.append([mod_name, mod_params])
            xmlnode = self.xml.nextNode(xmlnode)
         
         gdate = datetime.datetime.today()
         ctx = open( self.datdir + "ctl-can-config-skel.sh" ).readlines()
         out = open(fname,"w")
         
         for l in ctx:
             if re.search("{MOD_PROBE}",l):
                l = self.gen_modprobe_string(modlist,l)
             
             if re.search("{MOD_REMOVE}",l):
                l = self.gen_rmmod_string(modlist,l)
             
             if re.search("{GENDATE}",l):
                l = re.sub("{GENDATE}",gdate.ctime(),l)		   
             
             out.write(l)
         
         out.close()
    
    def gen_modprobe_string(self,modlist,l):
        s = ""
        for m in modlist:
            t = "modprobe %s %s"%(m[0],m[1])
            s += re.sub("{MOD_PROBE}", t, l)
        return s
    
    def gen_rmmod_string(self,modlist,l):
        s = ""
        for m in modlist:
            s += re.sub("{MOD_REMOVE}", str("modprobe -r " + m[0]),l)
        return s
    
    def get_outfilename(self, xmlnode):
        nname = xmlnode.prop("ip").lower()
        # некорректная проверка на то, что это IP
        # надо потом переделать на регулярное выражение
        if nname.find(".") != -1:
            nname = xmlnode.prop("name").lower()
        return "ctl-can-" + nname + ".sh"

if __name__ == "__main__":

    from can_conf import *
    from cmd_param import *

    is_system_run_flag = sys.argv[0].startswith("./")
    datdir = ( "/usr/share/uniset-configurator/" if not is_system_run_flag else "./" )
    templdir=( datdir + "templates/can/" if not is_system_run_flag else "./templates/" )

    confile = ""
    if checkArgParam("--help",False) == True or checkArgParam("-h",False) == True:
       print "Usage: %s [--confile configure.xml ] [--outfile filename]  --gen-can-conf Nodename" % sys.argv[0]
       print "--confile confile           - Configuration file. Default: configure.xml"
       print "--gen-can-conf nodename     - Generate ctl-can-config.sh for nodename."
       print "--outfile filename          - Save to filename. Default: ctl-can-'nodename'"
       print "-v                          - Verbose mode"
       exit(0)

    confile = getArgParam("--confile","configure.xml")
    nodename = getArgParam("--gen-can-conf","")
    verb = checkArgParam("-v",False)
    
    if nodename == "":
       print "Usage: %s [--confile configure.xml ] [--outfile filename]  --gen-can-conf Nodename" % sys.argv[0]
       exit(1)
    
    outfile = getArgParam("--outfile","")
    
    xml = UniXML.UniXML(confile)
    
    xmlnode = xml.findNode(xml.getDoc(),"nodes")[0].children.next
    while xmlnode != None:
       if xmlnode.prop("name") == nodename:
          break;
       xmlnode = xml.nextNode(xmlnode)
    
    if xmlnode == None:
       print "%s not found in <nodes> (confile: %s)" % (nodename,confile)
       exit(1)
    
    cannode = xml.findNode(xmlnode,"can")[0]
    if cannode:
       if not cannode.children:
          print "<can> section empty! for node='%s' (confile: %s)" % (nodename,confile)
          exit(1)
       cannode = cannode.children.next

    if cannode == None:
       print "<can> not found for node='%s' (confile: %s)" % (nodename,confile)
       exit(1)

    canconf = CANConfig(xml,templdir)

    if outfile == "":
       outfile = canconf.get_outfilename(xmlnode)

    canconf.gen_conf_script(cannode,outfile)
    
    if verb == True:
       print "Generate %s OK." % outfile
