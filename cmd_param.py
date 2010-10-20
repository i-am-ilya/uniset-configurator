# -*- coding: utf-8 -*-
import sys

def get_int_val(str_val):
        if str_val == "" or str_val == None: 
            return 0
        return int(str_val)

def getArgParam(param,defval=""):
    for i in range(0, len(sys.argv)):
        if sys.argv[i] == param:
           if i+1 < len(sys.argv):
              return sys.argv[i+1]
           else:
              break;
        
    return defval
    
def getArgInt(param,defval=0):
    for i in range(0, len(sys.argv)):
        if sys.argv[i] == param:
           if i+1 < len(sys.argv):
              return get_int_val(strsys.argv[i+1])
           else:
              break;
      
    return defval
    
def checkArgParam(param,defval=""):
    for i in range(0, len(sys.argv)):
        if sys.argv[i] == param:
           return True
      
    return defval
