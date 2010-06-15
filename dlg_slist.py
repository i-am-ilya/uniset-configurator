# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML

class SListDialog():

    xml = None

    def __init__(self, xml):

        self.xml = xml
        #                          ID|Name|Textname|xmlnode
        self.model = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,object)

        self.tv = gtk.TreeView()
        self.tv.set_model(self.model)
        self.tv.set_search_equal_func(self.sfunc)
         			
        self.tv.get_selection().set_mode(gtk.SELECTION_SINGLE)

        self.tv.set_rules_hint(True)
        self.tv.connect("button-press-event", self.on_button_press_event)

        self.add_columns()

        # expand all rows after the treeview widget has been realized
#       self.connect('realize', lambda tv: tv.expand_all())

        self.build_tree()

        self.tv.show_all()

        self.dlg = gtk.Dialog(_("Sensors list"),None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,(gtk.STOCK_OK,gtk.RESPONSE_OK,gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
        self.dlg.set_default_size(500,400)
        scwin = gtk.ScrolledWindow();
        scwin.add(self.tv)
        scwin.show_all()
        self.dlg.vbox.pack_start(scwin, True, True, 0)

    def reopen(self,xml):
        self.model.clear()
        self.build_tree()	    

    def build_tree(self):

        node = self.xml.findNode(self.xml.getDoc(),"sensors")[0].children.next 
        while node != None:
            self.model.append([node.prop("id"),node.prop("name"),node.prop("textname"),node])
            node = self.xml.nextNode(node)

    def sfunc(self,model, column, key, iter):

        if model.get_value(iter,0).find(key) != -1:
        	return False
        if model.get_value(iter,1).find(key) != -1:
            return False
#       if model.get_value(iter,2).find(key) != -1:
#           return False

        return True

    def add_columns(self):
        
        renderer = gtk.CellRendererText()
#        renderer.set_property("xalign", 0.0)
        column = gtk.TreeViewColumn(_("ID"), renderer, text=0)
        column.set_clickable(False)
        self.tv.append_column(column)

        renderer = gtk.CellRendererText()
#        renderer.set_property("xalign", 0.0)
        column = gtk.TreeViewColumn(_("Name"), renderer, text=1)
        column.set_clickable(False)
        self.tv.append_column(column)

        renderer = gtk.CellRendererText()
#        renderer.set_property("xalign", 0.0)
        column = gtk.TreeViewColumn(_("TextName"), renderer, text=1)
        column.set_clickable(False)
        self.tv.append_column(column)

    def on_button_press_event(self, object, event):                                                                                                                                 
        if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:                                                                                                              
            (model, iter) = self.tv.get_selection().get_selected()                                                                                                                         
            if not iter:                                                                                                                                                                
                 return False

            self.dlg.response(gtk.RESPONSE_OK)			
        return False

    def set_selected_xmlnode(self, sel):
        ts = self.tv.get_selection()
        ts.unselect_all()
        it = self.model.get_iter_first()
        while it is not None:
            if self.model.get_value(it, 3) == sel: # check iterator
                ts.select_iter(it)
                self.tv.scroll_to_cell( self.model.get_path(it) )
                return
            it = self.model.iter_next(it)
    
    def set_selected_name(self, sel):
        ts = self.tv.get_selection()
        ts.unselect_all()
        it = self.model.get_iter_first()
        while it is not None:
            if self.model.get_value(it, 1) == sel:
                ts.select_iter(it)
                self.tv.scroll_to_cell( self.model.get_path(it) )
                return
            it = self.model.iter_next(it)

    def set_selected_id(self, sel):
        ts = self.tv.get_selection()
        ts.unselect_all()

        it = self.model.get_iter_first()
        while it is not None:
            if self.model.get_value(it,0) == sel:
                ts.select_iter(it)
                self.tv.scroll_to_cell( self.model.get_path(it) )
                return
            it = self.model.iter_next(it)
    
    def run(self,rootwin, xmlnode=None):
#        if rootwin:
#            self.dlg.set_transient_for(rootwin)
        if xmlnode != None:
           self.set_selected_xmlnode(xmlnode)

#        self.dlg.maximize()
        res = self.dlg.run()
        self.dlg.hide();

        if res == gtk.RESPONSE_OK:  
          (model, iter) = self.tv.get_selection().get_selected()
          if iter:                                                                                                                                                                
              return model.get_value(iter,3)

        return None
