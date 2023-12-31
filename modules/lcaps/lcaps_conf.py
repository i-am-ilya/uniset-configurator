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
Генератор тестовых скриптов для свето-звуковой колонки
'''
class LCAPSConfig():

    def __init__(self,xml,datdir):
        self.xml = xml
        self.datdir = datdir
        self.copy_templates_flag = False
    
    def gen_test_skel(self,lcname,fname):
        
        self.settings_node = self.xml.findNode(self.xml.getDoc(),"settings")[0]
        if self.settings_node == None:
            print "<settings> not found?!..."
            return False
        
        lc_node = None
        node = self.xml.firstNode(self.settings_node.children)
        while node != None:
            if node.name.upper() == "LCAPS":
               name = to_str(node.prop("name"))
               if lcname == "ALL":
                  fname = "lcaps-%s-test.xml"%name.lower()
                  self.gen_test_skel_by_name(node,name,fname)
               elif name == lcname:
                  self.gen_test_skel_by_name(node,name,fname)
                  break
            
            node = self.xml.nextNode(node)
        
        # и скопировать сами тестовые шаблоны
        if self.copy_templates_flag == True:
           self.copy_templates(self.datdir,"./")
         
    
    def gen_test_skel_by_name(self, lc_node, lc_name, fname):
        
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
        
        reset_list = self.gen_reset_set(lc_node,o_node,g_node,r_node)
        
        ctx = open( self.datdir + "lcaps-test-skel.xml" ).readlines()
        ctx_item = open( self.datdir + "lcaps-test-skel-item.xml" ).readlines()
        ctx_check = open( self.datdir + "lcaps-test-skel-check.xml" ).readlines()
         
        tests = self.gen_tests_for_section(ctx_item,ctx_check,o_node,2)
        tests += self.gen_tests_for_section(ctx_item,ctx_check,r_node,3)
        tests += self.gen_tests_for_section(ctx_item,ctx_check,g_node,4)
        tests = self.gen_result_ctx(ctx,lc_node,tests,reset_list)
        
        out = open(fname,"w")
        out.write(tests)
        out.close()
        
    def copy_templates(self, datdir, todir):
        flist = ["lcaps-template.xml","lcaps-template-noconfirm.xml","lcaps-template-nohorn.xml"]
        
        for f in flist:
            self.copy_file(datdir+f, todir+f)
    
    def copy_file(self, src, dest):
        f_src=file(src,'rb')
        f_dest=file(dest,'wb')
        f_src.seek(0)
        f_dest.write(f_src.read())
        f_src.close()
        f_dest.close()	  
    
    def gen_reset_set_for_section(self,lc_node,sec_node):
        res = ""
        node = self.xml.firstNode(sec_node.children)
        while node != None:
           lamp = to_str(node.prop("lamp"))
           aps = to_str(node.prop("name"))
           if aps != "":
              res += aps + "=0 "
           if lamp != "":
              res += lamp + "=0 "
           node = self.xml.nextNode(node)
        
        res = res.strip().replace(" ",",")
        return res
    
    def gen_reset_set(self,lc_node,o_node,g_node,r_node):
        
        res1 = self.gen_reset_set_for_section(lc_node,o_node)
        res2 = self.gen_reset_set_for_section(lc_node,g_node)
        res3 = self.gen_reset_set_for_section(lc_node,r_node)
        res = str(res1 + "," + res2 + "," + res3)
        res = res.replace(",,",",")
        if res.endswith(","): res = res[:-1]
        if res.startswith(","): res = res[1:]
           
        return res.strip()
    
    def check_and_replace(self,s,t,v):
        if s == None or t == None or v == None:
           return s	  
        
        if t in s:
           return s.replace(t,v)
        return s
    
    def gen_result_ctx(self,ctx,lc_node,tests,rlist):
        res = ""
        gdate = datetime.datetime.today().strftime("uniset-configurator: %Y-%m-%d %H:%M")
        for l in ctx:
            l = self.check_and_replace(l,"{TESTS}",tests)
            l = self.check_and_replace(l,"{HORNRESET}",lc_node.prop("hornreset"))
            l = self.check_and_replace(l,"{HORN}",lc_node.prop("horn"))
            l = self.check_and_replace(l,"{CONFIRM}",lc_node.prop("confirm"))
            l = self.check_and_replace(l,"{LCNAME}",lc_node.prop("name").lower())
            l = self.check_and_replace(l,"{GENTIME}",gdate)
            l = self.check_and_replace(l,"{RLIST}",rlist)
            res += l   
        return res

    def gen_tests_for_section(self,ctx_item,ctx_check,secnode,tnum):
        res=""
        check = self.gen_checks_for_section(ctx_check,secnode)
        ignore = ""
        if check == "":
           ignore="1"
        
        for l in ctx_item:
            l = self.check_and_replace(l,"{TESTNUM}",str(tnum))
            l = self.check_and_replace(l,"{LCNAME}",secnode.parent.prop("name").upper())
            l = self.check_and_replace(l,"{SEC}",secnode.name.upper())
            l = self.check_and_replace(l,"{Flash}",secnode.prop("flamp"))
            l = self.check_and_replace(l,"{CommHorn}",secnode.prop("horn1"))
            l = self.check_and_replace(l,"{CHECK}",check)
            l = self.check_and_replace(l,"{IGN}",ignore)
            res += l   
        
        return res
        
    def gen_checks_for_section(self,ctx_check,secnode):
        res=""
        secname = secnode.name
        node = self.xml.firstNode(secnode.children)
        while node != None:
            nohorn= to_int(node.prop("nohorn"))
            t_postfix = ""
            if nohorn != 0:
               t_postfix = "-nohorn"
            
            noconfirm = to_int(node.prop("noconfirm"))
            if noconfirm != 0:
               t_postfix = "-noconfirm"
            
            if nohorn and noconfirm:
               t_postfix = "-nohorn-noconfirm"

            t_delay = node.prop("delay")
            if t_delay is None or len(t_delay) == 0:
                t_delay="0"

            for l in ctx_check:
                l = self.check_and_replace(l,'{LAMP}',node.prop("lamp"))
                l = self.check_and_replace(l,"{POSTFIX}",t_postfix)
                l = self.check_and_replace(l,"{SENSOR}",node.prop("name"))
                l = self.check_and_replace(l, "{DELAY}", t_delay)
                res += l
            node = self.xml.nextNode(node)
        
        return res
        

if __name__ == "__main__":

    from lcaps_conf import *
    from cmd_param import *

    is_system_run_flag = sys.argv[0].startswith("./")
    datdir = ( "/usr/share/uniset-configurator/" if not is_system_run_flag else "./" )
    templdir=( datdir + "templates/lcaps/" if not is_system_run_flag else "./templates/" )

    confile = ""
    if checkArgParam("--help",False) == True or checkArgParam("-h",False) == True:
       print "Usage: %s [--confile configure.xml ] [--outfile filename]  --gen-test-skel [name|ALL]" % sys.argv[0]
       print "--confile confile                 - Configuration file. Default: configure.xml"
       print "--gen-test-skel [LCAPSname|ALL]   - Generate test skeleton for LCAPS=name"
       print "--outfile filename                - Save to filename. Default: name-test"
       print "--copy-templates                  - Copy templates files."
       print "-v                                - Verbose mode"
       exit(0)

    confile = getArgParam("--confile","configure.xml")
    lcname = getArgParam("--gen-test-skel","")
    verb = checkArgParam("-v",False)
    
    if lcname == "":
       print "Usage: %s [--confile configure.xml ] [--outfile filename]  --gen-test-skel [name|ALL] [--copy-templates]" % sys.argv[0]
       exit(1)
    
    outfile = getArgParam("--outfile","")
    
    xml = UniXML.UniXML(confile)
    
    lcapsconf = LCAPSConfig(xml,templdir)
    lcapsconf.copy_templates_flag = checkArgParam("--copy-templates",False)
    
    if outfile == "":
       outfile = "lcaps-%s-test.xml"%lcname.lower()

    lcapsconf.gen_test_skel(lcname,outfile)
    if verb == True:
       print "Generate %s OK." % outfile
    
    exit(0)
