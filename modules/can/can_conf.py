#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
        c3["module"] = "elcus_can200mp"
        c3["textname"] = "Элкус CAN200MP"
        self.add_card(c3)
    
    def add_card(self,c):
        self.cards[c["name"]] = c

    def gen_conf_script(self,xmlnode,fname):
         cardsinfo = [] # [module,params,dev,baddr]
         modlist = {} # делаем словарь, чтобы исключить повторяющиеся модули..

         while xmlnode != None:
            mod_name = get_str_val(xmlnode.prop("module"))
            mod_params = get_str_val(xmlnode.prop("module_params"))
            if mod_name != "":
			   modlist[mod_name] = mod_name
            cardsinfo.append( [mod_name,mod_params,get_str_val(xmlnode.prop("dev")),get_str_val(xmlnode.prop("baddr"))] )
            xmlnode = self.xml.nextNode(xmlnode)
         
         gdate = datetime.datetime.today()
         ctx = open( self.datdir + "ctl-comedi-skel.sh" ).readlines()
         out = open(fname,"w")
         for l in ctx:
             if re.search("{MOD_PROBE}",l):
                l = self.gen_modprobe_string(modlist,l)
             
             if re.search("{MOD_REMOVE}",l):
                l = self.gen_rmmod_string(modlist,l)
             
             if re.search("{CARDS_CONFIG}",l):
                l = self.gen_cardsconf_string(cardsinfo,l)
             
             if re.search("{CARDS_REMOVE}",l):
                l = self.gen_rmcards_string(cardsinfo,l)
             
             if re.search("{GENDATE}",l):
                l = re.sub("{GENDATE}",gdate.ctime(),l)
             
             out.write(l)
         
         out.close()
    
    def gen_modprobe_string(self,modlist,l):
        s = ""
        for m in modlist:
            s += re.sub("{MOD_PROBE}", str("modprobe " + m),l)
        return s
    
    def gen_rmmod_string(self,modlist,l):
        s = ""
        for m in modlist:
            s += re.sub("{MOD_REMOVE}", str("rmmod " + m),l)
        return s
    
    def gen_rmcards_string(self,cardsinfo,l):
        s = ""
        for m in cardsinfo:
            dev = m[2]
            if dev == "":
               dev = "/dev/comedi???"
            s += re.sub("{CARDS_REMOVE}", str("/usr/sbin/comedi_config -r " + dev + " || RETVAL=1"),l)
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
            
            s += re.sub("{CARDS_CONFIG}", str("/usr/sbin/comedi_config " + dev + " " + mod + " " + ba + params + " || RETVAL=1"),l)
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
    templdir=datdir+"/templates/"

    confile = ""
    if checkArgParam("--help",False) == True or checkArgParam("-h",False) == True:
       print "Usage: %s [--confile configure.xml ] [--outfile filename]  --gen-comedi-conf Nodename" % sys.argv[0]
       print "--confile confile           - Configuration file. Default: configure.xml"
       print "--gen-comedi-conf nodename  - Generate ctl-comedi for nodename."
       print "--outfile filename          - Save to filename. Default: ctl-comedi-'nodename'"
       print "-v                          - Verbose mode"
       exit(0)

    confile = getArgParam("--confile","configure.xml")
    nodename = getArgParam("--gen-comedi-conf","")
    verb = checkArgParam("-v",False)
    
    if nodename == "":
       print "Usage: %s [--confile configure.xml ] [--outfile filename]  --generate-comedi-conf Nodename" % sys.argv[0]
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
    
    cardnode = xml.findNode(xmlnode,"iocards")[0].children.next
    if cardnode == None:
       print "<iocards> not found for node='%s' (confile: %s)" % (nodename,confile)
       exit(1)

    canconf = CANConfig(xml,templdir)

    if outfile == "":
       outfile = canconf.get_outfilename(xmlnode)

    canconf.gen_conf_script(cardnode,outfile)
    if verb == True:
       print "Generate %s OK." % outfile
   
