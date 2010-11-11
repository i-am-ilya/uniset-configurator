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
Класс реализующий всё что касается работы с настройками в/в (comedi):
1. Типы карт, параметры, модули ядра и т.п.
2. Он же консольный генератор скрипта настройки ctl-comedi.sx
'''
class IOConfig():

    def __init__(self,xml,datdir):
        self.xml = xml
        self.datdir = datdir
    
    def build_channels_list(self,cardnode,model,iter):
        cname = cardnode.prop("name").upper()
        if cname == "DI32":
            self.build_di32_list(cardnode,model,iter)
        if cname == "DO32":
            self.build_do32_list(cardnode,model,iter)
        elif cname == "AI16-5A-3" or cname == "AIC123xx" \
             or cname == "AIC120" or cname == "AIC121":
            self.build_ai16_list(cardnode,model,iter)
        elif cname == "AO16-xx":
            self.build_ao16_list(cardnode,model,iter)
        elif cname == "UNIO48":
            self.build_unio48_list(cardnode,model,iter)
        elif cname == "UNIO96":
            self.build_unio96_list(cardnode,model,iter)
   
    def build_di32_list(self,card,model,iter):
        for i in range(0,32):
            model.append(iter, [_("ch_")+str(i),"",None,_("channel"),str(i),"0"])

    def build_do32_list(self,card,model,iter):
        for i in range(0,32):
            model.append(iter, [_("ch_")+str(i),"",None,_("channel"),str(i),"0"])

    def build_ai16_list(self,card,model,iter):
        for i in range(0,8):
            model.append(iter, ["J2:"+str(i),"",None,_("channel"),str(i),"0"])
        for i in range(0,8):
            model.append(iter, ["J3:"+str(i),"",None,_("channel"),str(i),"1"])

    def build_ao16_list(self,card,model,iter):
        for i in range(0,8):
            model.append(iter, ["J2:"+str(i),"",None,_("channel"),str(i),"0"])
        for i in range(0,8):
            model.append(iter, ["J3:"+str(i),"",None,_("channel"),str(i),"1"])

    def build_unio48_list(self,card,model,iter):
        for i in range(0,24):
            model.append(iter, ["J1:"+str(i),"",None,_("channel"),str(i),"0"])
        for i in range(0,24):
            model.append(iter, ["J2:"+str(i),"",None,_("channel"),str(i),"1"])

    def build_unio96_list(self,card,model,iter):
        for i in range(0,24):
            model.append(iter, ["J1:"+str(i),"",None,_("channel"),str(i),"0"])
        for i in range(0,24):
            model.append(iter, ["J2:"+str(i),"",None,_("channel"),str(i),"1"])
        for i in range(0,24):
            model.append(iter, ["J3:"+str(i),"",None,_("channel"),str(i),"2"])
        for i in range(0,24):
            model.append(iter, ["J4:"+str(i),"",None,_("channel"),str(i),"3"])
    
    def get_params_for_aixx5a(self,cardnode):
        # последовательность параметров см. исходники модуля aixx5a
        cname = cardnode.prop("name").upper()
        avr = get_str_val(cardnode.prop("average"))
        if avr == "":
           avr = "1"
        if cname == "AIC120" or cname == "AIC121":
            return "0," + avr
        if cname == "AIC123" or cname == "AIC123XX":
            return "1," + avr
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
          sname = get_str_val(cardnode.prop(p))
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
        if cname == "AI16-5A-3" or cname == "AIC123XX" or cname == "AIC120" or cname == "AIC121":
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
            s += re.sub("{MOD_REMOVE}", str("rmmod -r " + m),l)
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

    ioconf = IOConfig(xml,templdir)

    if outfile == "":
       outfile = ioconf.get_outfilename(xmlnode)

    ioconf.gen_comedi_script(cardnode,outfile)
    if verb == True:
       print "Generate %s OK." % outfile
    
    exit(0)
