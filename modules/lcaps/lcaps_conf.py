#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
class LCAPSConfig():

    def __init__(self,xml,datdir):
        self.xml = xml
        self.datdir = datdir
    
    def gen_test_skel(self,lcname,fname):
        
        self.settings_node = self.xml.findNode(self.xml.getDoc(),"settings")[0]
        if self.settings_node == None:
            print "<settings> not found?!..."
            return False
        
        lc_node = None
        node = self.xml.firstNode(self.settings_node.children)
        while node != None:
            if node.name.upper() == "LCAPS":
               name = get_str_val(node.prop("name"))
               if name == lcname:
                  lc_node = node
                  break
            
            node = self.xml.nextNode(node)
         
        if lc_node == None:
           print "<LCAPS name='%s' not found"%lcname
           return False
         
        o_node = self.xml.findNode(lc_node,"orange")[0]
        if o_node == None:
           print "For '%s' <orange> section not found."%lc_name
           return
        g_node = self.xml.findNode(lc_node,"green")[0]
        if g_node == None:
           print "For '%s' <orange> section not found."%lc_name
           return
        r_node = self.xml.findNode(lc_node,"red")[0]
        if r_node == None:
           print "For '%s' <orange> section not found."%lc_name
           return
        
        ctx = open( self.datdir + "lcaps-test-skel.xml" ).readlines()
        ctx_item = open( self.datdir + "lcaps-test-skel-item.xml" ).readlines()
        ctx_check = open( self.datdir + "lcaps-test-skel-check.xml" ).readlines()
         
        tests = self.gen_tests_for_section(ctx_item,ctx_check,o_node,2)
        tests += self.gen_tests_for_section(ctx_item,ctx_check,r_node,3)
        tests += self.gen_tests_for_section(ctx_item,ctx_check,g_node,4)
        tests = self.gen_result_ctx(ctx,lc_node,tests)
        
        out = open(fname,"w")
        out.write(tests)
        out.close()
    
    def check_and_replace(self,s,t,v):
        if t in s:
           return s.replace(t,v)
        return s
    
    def gen_result_ctx(self,ctx,lc_node,tests):
        res = ""
        gdate = datetime.datetime.today().strftime("uniset-configurator: %Y-%m-%d %H:%M")
        for l in ctx:
            l = self.check_and_replace(l,"{TESTS}",tests)
            l = self.check_and_replace(l,"{HORNRESET}",lc_node.prop("hornreset"))
            l = self.check_and_replace(l,"{HORN}",lc_node.prop("horn"))
            l = self.check_and_replace(l,"{CONFIRM}",lc_node.prop("confirm"))
            l = self.check_and_replace(l,"{LCNAME}",lc_node.prop("name").lower())
            l = self.check_and_replace(l,"{GENTIME}",gdate)
            res += l   
        return res

    def gen_tests_for_section(self,ctx_item,ctx_check,secnode,tnum):
        res=""
        check = self.gen_checks_for_section(ctx_check,secnode)
        for l in ctx_item:
            l = self.check_and_replace(l,"{TESTNUM}",str(tnum))
            l = self.check_and_replace(l,"{LCNAME}",secnode.parent.prop("name"))
            l = self.check_and_replace(l,"{SEC}",secnode.name.upper())
            l = self.check_and_replace(l,"{Flash}",secnode.prop("flamp"))
            l = self.check_and_replace(l,"{CommHorn}",secnode.prop("horn1"))
            l = self.check_and_replace(l,"{CHECK}",check)
            res += l   
        
        return res
        
    def gen_checks_for_section(self,ctx_check,secnode):
        res=""
        secname = secnode.name
        node = self.xml.firstNode(secnode.children)
        while node != None:
            nohorn= get_int_val(node.prop("nohorn"))
            if nohorn != 0:
               nohorn = "-nohorn"
            else:
               nohorn = ""
            
            for l in ctx_check:
                l = self.check_and_replace(l,'{LAMP}',node.prop("lamp"))
                l = self.check_and_replace(l,"{NOHORN}",nohorn)
                l = self.check_and_replace(l,"{SENSOR}",node.prop("name"))
                res += l
            node = self.xml.nextNode(node)
        
        return res
        

if __name__ == "__main__":

    from lcaps_conf import *
    from cmd_param import *

    is_system_run_flag = sys.argv[0].startswith("./")
    datdir = ( "/usr/share/uniset-configurator/" if not is_system_run_flag else "./" )
    templdir=datdir+"/templates/lcaps"

    confile = ""
    if checkArgParam("--help",False) == True or checkArgParam("-h",False) == True:
       print "Usage: %s [--confile configure.xml ] [--outfile filename]  --gen-comedi-conf Nodename" % sys.argv[0]
       print "--confile confile           - Configuration file. Default: configure.xml"
       print "--gen-test-skel LCAPS name  - Generate test skeleton for LCAPS=name"
       print "--outfile filename          - Save to filename. Default: name-test"
       print "-v                          - Verbose mode"
       exit(0)

    confile = getArgParam("--confile","configure.xml")
    lcname = getArgParam("--gen-test-skel","")
    verb = checkArgParam("-v",False)
    
    if lcname == "":
       print "Usage: %s [--confile configure.xml ] [--outfile filename]  --gen-test-skel LCAPS_name" % sys.argv[0]
       exit(1)
    
    outfile = getArgParam("--outfile","")
    
    xml = UniXML.UniXML(confile)
    
    lcapsconf = LCAPSConfig(xml,templdir)
    
    if outfile == "":
       outfile = "lcaps-%s-test.xml"%lcname.lower()

    lcapsconf.gen_test_skel(lcname,outfile)
    if verb == True:
       print "Generate %s OK." % outfile
    
    exit(0)
