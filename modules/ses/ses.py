# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_editor
from global_conf import *
from ses_panel import *
from LinkEditor import *

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
   list_xmlnode = 5

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
            ["tv","tv_main",None,False],
            ["panel_popup","panel_popup",None,False],
            ["dlg_name","dlg_name",None,False],
            ["dlg_name_ent","dlg_name_ent",None,False],
            ["dlg_comm_ent","dlg_comm_ent",None,False]
        ]
        self.init_builder_elements(self.elements,self.builder)

        self.panel = SESPanel(conf)
        self.ses = LinkEditor(conf,conf.datdir+"sees.src.xml")
        self.sescontrol = LinkEditor(conf,conf.datdir+"seescontrol.src.xml")

        self.tv.reparent(self)

        self.model = None
        self.modelfilter = None
        self.model = gtk.TreeStore(gobject.TYPE_STRING,
                                    gobject.TYPE_STRING,
                                    gtk.gdk.Pixbuf,
                                    int,
                                    object,
                                    object)

        #self.model.append("SEESControl","",ot.scontrol,None)
        
        self.modelfilter = self.model.filter_new()
#       self.modelfilter.set_visible_column(1)

        # create treeview
        self.tv.set_model(self.model)
        self.tv.set_rules_hint(True)
        self.tv.connect("button-press-event", self.on_button_press_event)

        self.s_it = None
        self.p_it = None
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

            it = self.model.append(None,[nm,"",img_main,ot.scontrol,node,None])

            self.s_it = self.model.append(it,["Процессы управления","",img_ses_list,ot.seslist,None,None])
            self.read_ses_objects(node,self.s_it,it)
            self.p_it = self.model.append(it,["Панели управления","",img_panel_list,ot.panellist,None,None])
            self.read_panel_objects(node,self.p_it,it)

            node = self.conf.xml.nextNode(node)

    def read_ses_objects(self, main_node, iter, p_iter):
        mnode = self.conf.xml.firstNode(main_node.children)
        snode = self.conf.xml.findNode(mnode,"seslist")[0]
        if snode == None:
            print "(SESEditor::read_configuration): <seslist> for <SEESControl name='%s'...> not found?!..."%to_str(main_node.prop("name"))
            return

        self.model.set_value(iter,fid.xmlnode,snode)
        
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

            it = self.model.append(iter,[nm,"",img_ses,ot.ses,ses_node,node])

            node = self.conf.xml.nextNode(node)

    def read_panel_objects(self, main_node, iter, p_iter):
        mnode = self.conf.xml.firstNode(main_node.children)
        snode = self.conf.xml.findNode(mnode,"panellist")[0]
        if snode == None:
           print "(SESEditor::read_panel_objects): <panellist> for <SEESControl name='%s'...> not found?!..."%to_str(main_node.prop("name"))
           return

        self.model.set_value(iter,fid.xmlnode,snode)

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

            it = self.model.append(iter,[nm,"",img_panel,ot.panel,p_node,node])

            node = self.conf.xml.nextNode(node)
 
    def on_button_press_event(self, object, event):
#        print "*** on_button_press_event"
        (model, iter) = self.tv.get_selection().get_selected()

        if event.button == 3:
            if not iter:
               return False

            t = model.get_value(iter,fid.etype)
            if t == ot.panel:
               self.panel_popup.popup(None, None, None, event.button, event.time)
               return False

        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
           if not iter:
              return False
           t = model.get_value(iter,fid.etype)
           if t == ot.panel:
              self.edit(iter, self.panel)
           elif t == ot.ses:
              self.edit(iter, self.ses)
           elif t == ot.scontrol:
              self.edit(iter, self.sescontrol)
        return False

    def on_del_panel_activate(self, mitem):
        (model, iter) = self.tv.get_selection().get_selected()
        if not iter:
           return

        t = model.get_value(iter,fid.etype)
        if t!=ot.panel and t!=ot.ses:
           return
        
        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,_("Are you sure?"))
        res = dlg.run()
        dlg.hide()
        if res == gtk.RESPONSE_NO:
            return False
            

    def on_add_panel_activate(self, mitem):

        self.dlg_comm_ent.set_text("")
        self.dlg_name_ent.set_text("")

        res = self.dlg_name.run()
        self.dlg_name.hide()
        if res == gtk.RESPONSE_OK:
           return False

        nm = self.dlg_name_ent.get_text()
        if nm == "":
           return False

        comm = self.dlg_comm_ent.get_text()

        p_xmlnode = self.model.get_value(self.p_it,fid.xmlnode)
        node = p_xmlnode.newChild(None,"item",None)
        node.setProp("name",nm)

        xnode = self.create_new_panel(nm,comm)
        if not xnode:
           dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,"Не удалось создать xml-узел для панели")
           res = dlg.run()
           dlg.hide()
           return False

        img_panel = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_PANEL)
        it = self.model.append(self.p_it,[nm,"",img_panel,ot.panel,xnode,node])
        self.edit_panel(it)
        self.conf.mark_changes()

    def edit(self, iter, editor):
        xmlnode = self.model.get_value(iter,fid.xmlnode)
        if editor.run(xmlnode):
           self.model.set_value(iter,fid.name,xmlnode.prop("name"))
           p_node = self.model.get_value(iter,fid.list_xmlnode)
           if p_node:
              p_node.setProp("name",xmlnode.prop("name"))
           self.conf.mark_changes()

    def on_edit_panel_activate(self, mitem):
        pass

    def create_new_panel(self, nm, comm):
        xmlnode = self.settings_node.newChild(None,"SEESPanel",None)
        xmlnode.setProp("name",nm)
        xmlnode.setProp("comment",self.dlg_comm_ent.get_text())
        a_node = xmlnode.newChild(None,"APSPanel",None)
        a_node.setProp("name","APSPanel")
#        for i in self.panel_items:
#            x = a_node.newChild(None,"item",None)
#            x.setProp(i[0],i[1])

        return xmlnode

def create_module(conf):
    return SESEditor(conf)

def module_name():
    return "СЭС"
