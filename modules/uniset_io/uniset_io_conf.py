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
import os
from global_conf import *

'''
Класс реализующий всё что касается работы с настройками в/в (comedi):
1. Типы карт, параметры, модули ядра и т.п.
2. Он же консольный генератор скрипта настройки ctl-comedi.sx
'''
class IOConfig():

    def __init__(self,xml,datdir):
        self.xml = xml
        self.datdir = datdir
        self.templdir = self.datdir + "templates/"
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
                self.cardlist[cname] = editor

    def get_channel_list(self, cardnode):
        cname = cardnode.prop("name").upper()
        if cname in self.cardlist:
           editor = self.cardlist[cname]
           return editor.get_channel_list(cname)

        return [[0,"Unknown CARD","DI",0]]

    def like_ai16(self,cname):
        if cname == "AI16-5A-3" or cname == "AIC123XX/16" or \
           cname == "AIC120/16" or cname == "AIC121/16" or cname=="AI16":
            return True
         
        return False
    
    def like_ai8(self,cname):
         if cname == "AIC123XX/8" or cname == "AIC120/8" or cname == "AIC121/8":
            return True
         
         return False

    def like_aic123(self,cname):
        if cname == "AIC123XX/8" or cname == "AIC123XX/16" or cname == "AI16-5A-3":
           return True

        return False

    def like_aic120(self,cname):
        if cname == "AIC120/8" or cname == "AIC120/16":
           return True

        return False

    def like_aic121(self,cname):
        if cname == "AIC121/8" or cname == "AIC121/16":
           return True

        return False
    
    def build_ai8_list(self,card,model,iter,pic=None):
        for i in range(0,4):
            name = "Ch%d [J1:%d-%d]"%(i,2*i,2*i+1)
            model.append(iter, [name,"",None,_("channel"),str(i),"2",pic])
        for i in range(4,8):
            name = "Ch%d [J2:%d-%d]"%(i,2*(i-4),2*(i-4)+1)
            model.append(iter, [name,"",None,_("channel"),str(i),"2",pic])

    def get_iotype(self,cname,channel):
        cname = cname.upper()
        if cname == "DI32":
           return "DI"
        
        if cname == "DO32":
           return "DO"
        
        if self.like_ai16(cname) or self.like_ai8(cname):
           return "AI"
        
        if cname == "AO16-XX" or cname=="AO16":
           return "AO"
        
        # к UNIO можно водключать любые сигналы... 
        # поэтому должно быть более иннтелектуально...
        # но пока для простоты сделаем по умолчанию DI
        if cname == "UNIO48" or cname == "UNIO96":
           return "DI"
        
        return "DI"
   
    def get_default_channel_param(self,cname):
        cname = cname.upper()
        ret = dict()
        
        if self.like_ai16(cname):
           ret["aref"] = 0
           ret["range"] = 0
           return ret

        if self.like_ai8(cname):
           ret["aref"] = 2
           ret["range"] = 0
           return ret
        
#        if cname == "AO16-XX" or cname=="AO16":
        
        return ret
    
    def get_params_for_aixx5a(self,cardnode):
        # последовательность параметров см. исходники модуля aixx5a
        cname = cardnode.prop("name").upper()
        avr = to_str(cardnode.prop("average"))
        if avr == "":
           avr = "1"
        
        if self.like_aic123(cname):
            return "1," + avr

        if self.like_aic120(cname) or self.like_aic121(cname):
            return "0," + avr
        
        return ""
    
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
    
    def get_params_for_unioxx(self,cardnode):
        s = ""
        maxnum = 5
#        if cardnode.prop("name").upper() == UNIO48:
#            maxnum = 3
        for i in range(1,maxnum):
          p = "subdev" + str(i)
          sname = to_str(cardnode.prop(p))
          if s != "":
             s = s + "," + self.get_typenum_for_unio_subdev(sname.upper())
          else:
             s = self.get_typenum_for_unio_subdev(sname.upper())
        
        return s
    
    def get_module_params_for_card(self,cardnode):
        cname = cardnode.prop("name").upper()
        
        if cname == "DI32":
            return ["di32_5",""]
        if cname == "DO32":
            return ["do32",""]
        if self.like_ai16(cname) or self.like_ai8(cname):
            return ["aixx5a", self.get_params_for_aixx5a(cardnode) ]
        if cname == "AO16-XX":
            return ["ao16",""]
        if cname == "UNIO48":
            return ["unioxx5", self.get_params_for_unioxx(cardnode)]
        if cname == "UNIO96":
            return ["unioxx5", self.get_params_for_unioxx(cardnode)]
        
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

    ioconf = IOConfig(xml,datdir)

    if outfile == "":
       outfile = ioconf.get_outfilename(xmlnode)

    ioconf.gen_comedi_script(cardnode,outfile)
    if verb == True:
       print "Generate %s OK." % outfile
    
    exit(0)
