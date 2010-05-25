# -*- coding: utf-8 -*-
from gettext import gettext as _
import gtk
import UniXML

class IOCards():

    xml = None

    def __init__(self):
    	pass

    def build_channels_list(self,cardnode,model,iter):
        if cardnode.prop("name") == "DI32":
            self.build_di32_list(cardnode,model,iter)
        elif cardnode.prop("name") == "AI16":
            self.build_ai16_list(cardnode,model,iter)
    
    def build_di32_list(self,cardnode,model,iter):
        for i in range(0,32):
            model.append(iter, [_("channel")+str(i),"",cardnode])
 
    def build_ai16_list(self,cardnode,model,iter):
		for i in range(0,16):
			model.append(iter, [_("channel")+str(i),"",cardnode])
