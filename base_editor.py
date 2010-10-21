# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import gobject
import UniXML
import configure

from global_conf import *


'''
Базовый класс для модулей...
Основная работа - это считать парметры из
xml-файла, отобразить их в диалоге настройки, проверить
корректность и потом сохранить обратно в файл.
При этом, т.к. с каждым параметром идёт по сути 
"однотипная" работа, то используется следующая идея:
Создан общий список (несколько списков) параметров,
содержащий информацию:
- название glade-элемента в диалоге настройки
- название параметра в xml-файле
- название поля в данном классе
- игнорировать ли запись поля в xml-файл
И вся работа ведётся со списком параметров.
См. функции:
init_glade_elements()
init_elements_value()
validate_elements()
save2xml_elements_value()
'''
class BaseEditor():

    def __init__(self, conf):

        self.conf = conf

    def init_glade_elements(self, elist):
        ''' Инициализация переменных из glade файла...
            по списку элементов вида [class field,gladename,xmlname,xml_save_ignore]'''
        for e in elist:
            if e[0] == None or e[1] == None:
                continue
            self.__dict__[e[0]] = self.conf.glade.get_widget(e[1])

    def init_elements_value(self,elist,snode):
        ''' Инициализация переменных из xml
            по списку элементов вида [class field,gladename,xmlname,xml_save_ignore]'''
        for e in elist:
            if e[0]==None or e[2] == None:
                continue
            cname = str(self.__dict__[e[0]].__class__.__name__)
            if cname == "SpinButton":
                self.__dict__[e[0]].set_value(get_int_val(snode.prop(e[2])))
            elif cname == "Entry":
                self.__dict__[e[0]].set_text(get_str_val(snode.prop(e[2])))
            elif cname == "CheckButton":
                self.__dict__[e[0]].set_active(get_int_val(snode.prop(e[2])))
            elif cname == "ComboBox":
                self.set_combobox_element(self.__dict__[e[0]], get_str_val(snode.prop(e[2])))
            elif cname == "Label":
                self.__dict__[e[0]].set_text(get_str_val(snode.prop(e[2])))
       
    def validate_elements(self,elist):
        ''' Проверка корректности данны 
            по списку элементов вида [class field,gladename,xmlname,xml_save_ignore]'''
        for e in elist:
            if e[0]==None or e[2] == None:
                continue
            cname = str(self.__dict__[e[0]].__class__.__name__)
            if cname == "Entry":
                s = self.__dict__[e[0]].get_text()
                if s!="" and check_value_int(s) == False:
                      return [False,e[2]]

        return [True,""]
    
    def save2xml_elements_value(self,elist,snode,setval=None):
        ''' Сохранение переменных в xml-узел
            по списку элементов вида [class field,gladename,xmlname,xml_save_ignore]'''
        for e in elist:
            if e[0]==None or e[2] == None or e[3]==True:
                continue
            if setval != None:
                snode.setProp(e[2],setval)
            else:
                cname = str(self.__dict__[e[0]].__class__.__name__)
                if cname == "CheckButton":
                    snode.setProp(e[2],self.get_cb_param(self.__dict__[e[0]]))
                elif cname == "Entry":
                    snode.setProp(e[2],self.__dict__[e[0]].get_text())
                elif cname == "Label":
                    snode.setProp(e[2],self.__dict__[e[0]].get_text())
                elif cname == "SpinButton":
                    v = self.__dict__[e[0]].get_value_as_int()
                    if v == 0:
                        snode.setProp(e[2],"")
                    else:
                        snode.setProp(e[2],str(v))
                elif cname == "ComboBox":
                    t = self.__dict__[e[0]].get_active_text()
                    if t == "" or t == "None":
                        snode.setProp(e[2],"")
                    else:
                        snode.setProp(e[2],t)
    
    def get_cb_param(self, checkbutton):
        if checkbutton.get_active():
            return "1"
        return ""
    
    def set_combobox_element(self,cbox,val):
        if val == None:
            val = ""
        model = cbox.get_model()
        it = model.get_iter_first()
        while it is not None:                     
            if val.upper() == str(model.get_value(it,0)).upper():
                 cbox.set_active_iter(it)
                 return
            it = model.iter_next(it)
