# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_editor
from global_conf import *
from ses_panel import *

class ot():
   scontrol = 1
   ses = 2
   panel = 3
   seslist = 4
   panellist = 5
   
class fid():
   name = 0
   info = 1
   pic = 2
   etype = 3
   xmlnode = 4

pic_MAIN = 'ses_main.png'
pic_SES_LIST = 'ses_main.png'
pic_SES = 'ses.png'
pic_PANEL_LIST = 'ses_main.png'
pic_PANEL = 'ses_panel.png'

class SESEditor(base_editor.BaseEditor, gtk.Viewport):

    def __init__(self, conf):

        gtk.Viewport.__init__(self)
        base_editor.BaseEditor.__init__(self,conf)

        self.builder = gtk.Builder()
        self.builder.add_from_file(conf.datdir+"seseditor.ui")
        self.builder.connect_signals(self)
  
        self.elements=[
            ["tv","tv_main",None,False]
        ]
        self.init_builder_elements(self.elements,self.builder)

        self.panel = SESPanel(conf)

        self.tv.reparent(self)

        self.model = None
        self.modelfilter = None
        self.model = gtk.TreeStore(gobject.TYPE_STRING,
                                    gobject.TYPE_STRING,
                                    gtk.gdk.Pixbuf,
                                    int,
                                    object)

        #self.model.append("SEESControl","",ot.scontrol,None)
        
        self.modelfilter = self.model.filter_new()
#       self.modelfilter.set_visible_column(1)

        # create treeview
        self.tv.set_model(self.model)
        self.tv.set_rules_hint(True)
        self.tv.connect("button-press-event", self.on_button_press_event)

        self.read_configuration()
    
    def reopen(self):
#        self.model.clear()
#        self.show_all()
        pass

    def read_configuration(self):
        self.settings_node = self.conf.xml.findNode(self.conf.xml.getDoc(),"settings")[0]
        if self.settings_node == None:
            print "(SESEditor::read_configuration): <settings> not found?!..."
            return

        node = self.conf.xml.firstNode(self.settings_node.children)
        img_main = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_MAIN)
        img_ses_list = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_SES_LIST)
        img_panel_list = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_PANEL_LIST)
        while node != None:
            if node.name.upper() != "SEESCONTROL":
               node = self.conf.xml.nextNode(node)
               continue

            nm = to_str(node.prop("name"))
            if nm == "":
               nm = "SEESControl"

            it = self.model.append(None,[nm,"",img_main,ot.scontrol,node])

            s_it = self.model.append(it,["Процессы управления","",img_ses_list,ot.seslist,None])
            self.read_ses_objects(node,s_it,it)
            p_it = self.model.append(it,["Панели управления","",img_panel_list,ot.panellist,None])
            self.read_panel_objects(node,p_it,it)

            node = self.conf.xml.nextNode(node)

    def read_ses_objects(self, main_node, iter, p_iter):
        mnode = self.conf.xml.firstNode(main_node.children)
        snode = self.conf.xml.findNode(mnode,"seslist")[0]
        if snode == None:
            print "(SESEditor::read_configuration): <seslist> for <SEESControl name='%s'...> not found?!..."%to_str(main_node.prop("name"))
            return
        self.model.set_value(p_iter,fid.xmlnode,snode)
         
        
        img_ses = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_SES)
        node = self.conf.xml.firstNode(snode.children)
        if node == None:
           return

        while node != None:
            nm = to_str(node.prop("name"))
            if nm == "":
               print "(SESEditor::read_ses_objects): empty name?!! in <seslist> for <SEESControl name='%s'>"%to_str(main_node.prop("name"))
               node = self.conf.xml.nextNode(node)
               continue

            ses_node = self.conf.xml.findNode_byPropValue(self.settings_node.children,nm,nm,"name",False)[0]
            if not ses_node:
               print "(SESEditor::read_ses_objects): Not found SES! name=%s for <SEESControl name='%s'>"%(nm,to_str(main_node.prop("name")))
               node = self.conf.xml.nextNode(node)
               continue

            it = self.model.append(iter,[nm,"",img_ses,ot.ses,ses_node])

            node = self.conf.xml.nextNode(node)

    def read_panel_objects(self, main_node, iter,p_iter):
        mnode = self.conf.xml.firstNode(main_node.children)
        snode = self.conf.xml.findNode(mnode,"panellist")[0]
        if snode == None:
            print "(SESEditor::read_panel_objects): <panellist> for <SEESControl name='%s'...> not found?!..."%to_str(main_node.prop("name"))
            return
        self.model.set_value(p_iter,fid.xmlnode,snode)

        img_panel = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_PANEL)
        node = self.conf.xml.firstNode(snode.children)
        if node == None:
           return

        while node != None:
            nm = to_str(node.prop("name"))
            if nm == "":
               print "(SESEditor::read_panel_objects): empty name?!! in <panellist> for <SEESControl name='%s'>"%to_str(main_node.prop("name"))
               node = self.conf.xml.nextNode(node)
               continue

            p_node = self.conf.xml.findNode_byPropValue(self.settings_node.children,nm,nm,"name",False)[0]
            if not p_node:
               print "(SESEditor::read_panel_objects): Not found SEESPanel! name=%s for <SEESControl name='%s'>"%(nm,to_str(main_node.prop("name")))
               node = self.conf.xml.nextNode(node)
               continue

            it = self.model.append(iter,[nm,"",img_panel,ot.panel,p_node])

            node = self.conf.xml.nextNode(node)
 
    def on_button_press_event(self, object, event):
#        print "*** on_button_press_event"
        (model, iter) = self.tv.get_selection().get_selected()

        if event.button == 3:
            if not iter:
#                 self.empty_popup.popup(None, None, None, event.button, event.time)
                 return False

#            t = model.get_value(iter,fid.etype)

        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
           if not iter:
              return False
           t = model.get_value(iter,fid.etype)
           if t == ot.panel and self.panel.run(model.get_value(iter,fid.xmlnode)):
              self.mark_changes()

        return False


def create_module(conf):
    return SESEditor(conf)

def module_name():
    return "СЭС"
