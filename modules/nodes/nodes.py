# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure
import base_editor

pic_NODE = 'node.png'

class fid():
  name = 0
  text = 1
  xmlnode = 2
  pic = 3

'''
Редактирование списка узлов
'''
class NodesEditor(base_editor.BaseEditor,gtk.TreeView):

    def __init__(self, conf):
        
        gtk.TreeView.__init__(self)
        base_editor.BaseEditor.__init__(self,conf)

        self.glade = gtk.glade.XML(conf.datdir+"nodes.glade")
        self.glade.signal_autoconnect(self)

        # --------  my signals ------------
#        gobject.type_register(NodesEditor)
        gobject.signal_new("change-node", NodesEditor, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (object,))
        gobject.signal_new("add-new-node", NodesEditor, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (object,))
        gobject.signal_new("remove-node", NodesEditor, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (object,))
        # ---------------------------------
        conf.set_nodes_editor(self)
       
        self.model = None
        self.modelfilter = None
        #                          Name | Parameters | xmlnode | pic
        self.model = gtk.TreeStore(gobject.TYPE_STRING,gobject.TYPE_STRING,object,gtk.gdk.Pixbuf)
        self.modelfilter = self.model.filter_new()

#        self.modelfilter.set_visible_column(1)

        # create treeview
        self.set_model(self.model)
        self.set_rules_hint(True)
        self.connect("button-press-event", self.on_button_press_event)

        column = gtk.TreeViewColumn(_("Name"))
        nmcell = gtk.CellRendererText()
        pbcell = gtk.CellRendererPixbuf()
        column.pack_start(pbcell, False)
        column.pack_start(nmcell, False)
        column.set_attributes(pbcell,pixbuf=fid.pic)
        column.set_attributes(nmcell,text=fid.name)
        column.set_clickable(False)
        self.append_column(column)
        
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Parameters"), renderer, text=fid.text)
        column.set_clickable(False)
        self.append_column(column)

        # expand all rows after the treeview widget has been realized
#       self.connect('realize', lambda tv: tv.expand_all())

        self.menu_list = [ \
            ["node_popup","nodes_popup",None,True] \
        ]
        self.init_glade_elements(self.menu_list,self.glade)
        
        self.params = [ \
            ["dlg","nodes_dlg",None,True], \
            ["n_id","nodes_id","id",False], \
            ["n_name","nodes_name","name",False], \
            ["n_tname","nodes_tname","textname",False], \
            ["n_ip","nodes_ip","ip",False] \
        ]
        self.init_glade_elements(self.params,self.glade)

        self.build_tree()
    
    def reopen(self):
        self.model.clear()
        self.build_tree() 
    
    def get_info(self,xmlnode):
        return str("id=" + str(xmlnode.prop("id")) + " ip=" + xmlnode.prop("ip"))

    def build_tree(self):
        node = self.conf.xml.findNode(self.conf.xml.getDoc(),"nodes")[0].children.next 
        img = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_NODE)
        while node != None:
            iter1 = self.model.append(None,[node.prop("name"),self.get_info(node),node,img])
            node = self.conf.xml.nextNode(node)

    def on_button_press_event(self, object, event):                                                                                                                                 
#        print "*** on_button_press_event"
        (model, iter) = self.get_selection().get_selected()

        if event.button == 3:                                                                                                                                                       
            if not iter: return False
            self.node_popup.popup(None, None, None, event.button, event.time)
            return False
        
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
            if not iter:                                                                                                                                                                
                 return False
            self.nodes_edit_node_activate(None)
        return False

    def on_nodes_btnCancel_clicked(self, button):
       self.dlg.response(gtk.RESPONSE_CANCEL)

    def on_nodes_btnOK_clicked(self,button):
       self.dlg.response(gtk.RESPONSE_OK)
    
    def nodes_genlist_activate(self,menuitem):
        
        dlg = gtk.FileChooserDialog(_("File save"),action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        dlg.set_current_name("nodelist.txt")
        res = dlg.run()
        dlg.hide()
        if res == gtk.RESPONSE_OK:
            f = open(dlg.get_filename(),"w");
            it = self.model.get_iter_first()
            while it is not None:
               xmlnode = self.model.get_value(it,fid.text)
               hname = str(xmlnode.prop("ip")) + '\n'
               f.write(hname)
               it = self.model.iter_next(it)	  
            f.close()
    
    def nodes_remove_node_activate(self,menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return
        
        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,_("Are you sure?"))
        res = dlg.run()
        dlg.hide()
        if res == gtk.RESPONSE_NO:
            return False
        
        xmlnode = model.get_value(iter,fid.xmlnode)
        try:
           self.emit("remove-node",xmlnode)
        except :
           pass
        
        xmlnode.unlinkNode()
        model.remove(iter)
        self.conf.mark_changes()
        self.conf.n_reopen()

    def nodes_add_node_activate(self,menuitem):
        node = self.conf.xml.findNode(self.conf.xml.getDoc(),"nodes")[0]
        if node == None:
            print "************** <nodes> not found ?!"
            return            
           
        xmlnode = node.newChild(None,"item",None)
        if xmlnode == None:
            print "************** FAILED CREATE <nodes> child item"
            return            
        
        if self.edit_node(xmlnode) == False:
            node.unlinkNode()
            return

        img = gtk.gdk.pixbuf_new_from_file(self.conf.imgdir+pic_NODE)
        self.model.append(None,[xmlnode.prop("name"),self.get_info(xmlnode),xmlnode,img])
        self.conf.mark_changes()
        self.conf.n_reopen()
        try:
           self.emit("add-new-node",xmlnode)
        except :
           pass
    
    def nodes_edit_node_activate(self,menuitem):
        (model, iter) = self.get_selection().get_selected()
        if not iter: return
        
        xmlnode = model.get_value(iter,fid.xmlnode)
        if self.edit_node(xmlnode) == True:
            model.set_value(iter,fid.name,xmlnode.prop("name"))
            model.set_value(iter,fid.text,self.get_info(xmlnode))
            self.conf.mark_changes()
            self.conf.n_reopen()
            try:
                self.emit("change-node",xmlnode)
            except :
                pass
        
    def edit_node(self,xmlnode):
        self.init_elements_value(self.params,xmlnode)
        while True:
            res = self.dlg.run()
            self.dlg.hide()
            if res != gtk.RESPONSE_OK:
                return False
            
            # check name
            if self.n_name.get_text().strip() == "":
               dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING,gtk.BUTTONS_OK,_("Empty 'name'"))
               res = dlg.run()
               dlg.hide()
               continue

            # check id
            
            # check...
            
            break                

        self.save2xml_elements_value(self.params,xmlnode)
        return True


def create_module(conf):
    return NodesEditor(conf)

def module_name():
    return "Узлы"
