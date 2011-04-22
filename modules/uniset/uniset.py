# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_editor

def create_module(conf):
    return UniSetEditor(conf)

def module_name():
    return "UniSet"

'''
Редактирование общих параметров uniset
'''
class UniSetEditor(base_editor.BaseEditor,gtk.Viewport):

    def __init__(self, conf):
        
        base_editor.BaseEditor.__init__(self,conf)
        gtk.Viewport.__init__(self)

        self.glade = conf.glade
        self.glade.signal_autoconnect(self)
        
        nbook = self.glade.get_widget("uniset_nbook")
        nbook.reparent(self)
       
        self.connect("button-press-event", self.on_button_press_event)
        
        self.menu_list = [ \
            ["node_popup","nodes_popup",None,True] \
        ]
        #self.init_glade_elements(self.menu_list)
        # [0,            1          2            3        4        5     ]
        # [class_field,glade_name,xmlnodename,saveignore,xmlnode,propname]
        self.params = [ \
            ["lnode","uniset_lnode",None,True,None,None], \
            ["btn_lnode","uniset_btn_lnode",None,True,None,None], \
            ["root_sec","uniset_root_sec","RootSection",False,None,"name"], \
            ["serv_sec","uniset_serv_sec","ServicesSection",False,None,"name"], \
            ["ns_host","uniset_ns_host","NameService",False,None,"host"], \
            ["ns_port","uniset_ns_port","NameService",False,None,"port"], \
            ["localIOR","uniset_localIOR","LocalIOR",False,None,"name"], \
            ["msg_queue_size","uniset_msg_queue_size","SizeOfMessageQueue",False,None,"name"], \
            ["push_mutex","uniset_push_mutex","PushMutexTimeout",False,None,"name"], \
            ["recv_mutex","uniset_recv_mutex","RecvMutexTimeout",False,None,"name"], \
            ["wdt","uniset_wdt","WatchDogTime",False,None,"name"], \
            ["confdir","uniset_confdir","ConfDir",False,None,"name"], \
            ["datadir","uniset_datadir","DataDir",False,None,"name"], \
            ["logdir","uniset_logdir","LogDir",False,None,"name"], \
            ["bindir","uniset_bindir","BinDir",False,None,"name"], \
            ["docdir","uniset_docdir","DocDir",False,None,"name"], \
            ["lockdir","uniset_lockdir","LockDir",False,None,"name"], \
            ["net_cnt","uniset_net_cnt","CountOfNet",False,None,"name"], \
            ["repeat_cnt","uniset_repeat_cnt","RepeatCount",False,None,"name"], \
            ["repeat_timeout","uniset_repeat_timeout","RepeatTimeoutMS",False,None,"name"], \
            ["deb_lbl","uniset_deb_lbl","UniSetDebug",True,None,"name"], \
            ["deb_info","uniset_deb_info",None,True,None,None], \
            ["deb_warn","uniset_deb_warn",None,True,None,None], \
            ["deb_crit","uniset_deb_crit",None,True,None,None], \
            ["deb_sys","uniset_deb_sys",None,True,None,None], \
            ["deb_rep","uniset_deb_rep",None,True,None,None], \
            ["deb_l1","uniset_deb_l1",None,True,None,None], \
            ["deb_l2","uniset_deb_l2",None,True,None,None], \
            ["deb_l3","uniset_deb_l3",None,True,None,None], \
            ["deb_l4","uniset_deb_l4",None,True,None,None], \
            ["deb_l5","uniset_deb_l5",None,True,None,None], \
            ["deb_l6","uniset_deb_l6",None,True,None,None], \
            ["deb_l7","uniset_deb_l7",None,True,None,None], \
            ["deb_l8","uniset_deb_l8",None,True,None,None], \
            ["deb_l9","uniset_deb_l9",None,True,None,None] \
        ]
        self.init_glade_elements(self.params,self.glade)
        
        self.init_xmlnodes()
        self.init_params()
    
    def reopen(self):
        self.init_xmlnodes()
        self.init_params()
    
    def init_xmlnodes(self):
        for p in self.params:
            if p[2] != None:
               p[4] = self.conf.xml.findNode(self.conf.xml.getDoc(),p[2])[0]
               if p[4] == None:
                    print "WARNING: " + str(p[2]) + " not found.."

    def save_params(self):
        for p in self.params:
            if p[4] != None and p[2]!="" and p[3]!=True:
                l = [ p[0], p[1], p[5], p[3] ]
                self.save2xml_elements_value([ l ],p[4])

    def init_params(self):
        for p in self.params:
            if p[4] != None and p[2]!="" and p[3]!=True:
                l = [ p[0], p[1], p[5] ]
                self.init_elements_value([ l ],p[4])
    
    def on_button_press_event(self, object, event):
#        if event.button == 3:
#            return False
        
#        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
          
        return False
    
    def on_uniset_btn_lnode_clicked(self,button):
        print "**************** lnode clicked.."
    
    def on_uniset_btnCancel_clicked(self, button):
       self.dlg.response(gtk.RESPONSE_CANCEL)

    def on_uniset_btnOK_clicked(self,button):
       self.dlg.response(gtk.RESPONSE_OK)

def create_module(conf):
    return UniSetEditor(conf)

def module_name():
    return "UniSet"
