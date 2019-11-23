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
from global_conf import *

'''
Генератор тестов для АПС панели
'''
class APSPanelConfig():

    def __init__(self,xml,datdir):
        self.xml = xml
        self.datdir = datdir
    
    def gen_test_skel(self,pname,fname):
        
        self.settings_node = self.xml.findNode(self.xml.getDoc(),"settings")[0]
        if self.settings_node == None:
            print "<settings> not found?!..."
            return False
        
        node = self.xml.firstNode(self.settings_node.children)
        while node != None:
            if node.name.upper() == "APSPANEL":
               name = to_str(node.prop("name"))
               if pname == "ALL":
                  fname = "apspanel-%s-test.xml"%name.lower()
                  self.gen_test_skel_by_name(node,name,fname)
               elif name == pname:
                  self.gen_test_skel_by_name(node,name,fname)
                  break
            
            node = self.xml.nextNode(node)
    
    def gen_test_skel_by_name(self, p_node, p_name, fname):
        
        if p_node == None:
           print "<APSPanel name='%s' not found"%p_name
           return False
        
        print "******* gen for " + str(p_name)
        
        ctx = open( self.datdir + "apspanel-test-skel.xml" ).readlines()
        ctx_item = open( self.datdir + "apspanel-test-skel-item.xml" ).readlines()
        ctx_check = open( self.datdir + "apspanel-test-skel-check.xml" ).readlines()
         
        tests = self.gen_tests(ctx_item,ctx_check,p_node)
        tests = self.gen_result_ctx(ctx,p_node,tests)
        
        out = open(fname,"w")
        out.write(tests)
        out.close()
    
    def check_and_replace(self,s,t,v):
        if s == None or t == None or v == None:
           return s
        
        if t in s:
           return s.replace(t,v)
        return s
    
    def gen_result_ctx(self,ctx,node,tests):
        res = ""
        gdate = datetime.datetime.today().strftime("uniset-configurator: %Y-%m-%d %H:%M")
        for l in ctx:
            l = self.check_and_replace(l,"{TESTS}",tests)
            l = self.check_and_replace(l,"{HORNRESET}",node.prop("hornreset"))
            l = self.check_and_replace(l,"{HORN}",node.prop("horn"))
            l = self.check_and_replace(l,"{CONFIRM}",node.prop("confirm"))
            l = self.check_and_replace(l,"{NAME}",node.prop("name").lower())
            l = self.check_and_replace(l,"{GENTIME}",gdate)
            res += l   
        return res

    def gen_tests(self,ctx_item,ctx_check,node):
        res=""
        check = self.gen_checks(ctx_check,node)
        for l in ctx_item:
            l = self.check_and_replace(l,"{NAME}",node.prop("name").upper())
            l = self.check_and_replace(l,"{Flash}",node.prop("flamp"))
            l = self.check_and_replace(l,"{CommHorn}",node.prop("horn1"))
            l = self.check_and_replace(l,"{CHECK}",check)
            res += l   
        
        return res
        
    def gen_checks(self,ctx_check,p_node):
        res=""
        node = self.xml.firstNode(p_node.children)
        while node != None:
            nohorn= to_int(node.prop("nohorn"))
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

    from apspanel_conf import *
    from cmd_param import *

    is_system_run_flag = sys.argv[0].startswith("./")
    datdir = ( "/usr/share/uniset-configurator/" if not is_system_run_flag else "./" )
    templdir=( datdir + "templates/apspanel/" if not is_system_run_flag else "./templates/" )

    confile = ""
    if checkArgParam("--help",False) == True or checkArgParam("-h",False) == True:
       print "Usage: %s [--confile configure.xml ] [--outfile filename]  --gen-test-skel [name|ALL]" % sys.argv[0]
       print "--confile confile                 - Configuration file. Default: configure.xml"
       print "--gen-test-skel [panel name|ALL]  - Generate test skeleton for APSPanel name"
       print "--outfile filename                - Save to filename. Default: name-test"
       print "-v                                - Verbose mode"
       exit(0)

    confile = getArgParam("--confile","configure.xml")
    pname = getArgParam("--gen-test-skel","")
    verb = checkArgParam("-v",False)
    
    if pname == "":
       print "Usage: %s [--confile configure.xml ] [--outfile filename]  --gen-test-skel [name|ALL]" % sys.argv[0]
       exit(1)
    
    outfile = getArgParam("--outfile","")
    
    xml = UniXML.UniXML(confile)
    
    apsconf = APSPanelConfig(xml,templdir)
    
    if outfile == "":
       outfile = "apspanel-%s-test.xml"%pname.lower()

    apsconf.gen_test_skel(pname,outfile)
    if verb == True:
       print "Generate %s OK." % outfile
