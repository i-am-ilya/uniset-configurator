# -*- coding: utf-8 -*-

import sys

# универсальный код для диалогов
# чтобы не делать обработку всех возможных кнопок 'OK'
# можно в glade назначать для всех 'OK'(в диалогах) заранее известный код возврата 
# (см. glade)
dlg_RESPONSE_OK = 100


# всякие полезные функции

def check_value_int(val):                                         
    try:
       x = int(val)
       return True
    except ValueError, NameError:
       return False
    
def to_int(str_val):
    if str_val == "" or str_val == None: 
       return 0
    return int(str_val)

def to_str(str_val):
    if str_val == None: 
       return ""
    return str(str_val)

def __line__():
    caller = inspect.stack()[1]
    return int (caller[2])

def __function__():
    caller = inspect.stack()[1]
    return caller[3]

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
              return to_int(strsys.argv[i+1])
           else:
              break;

    return defval

def checkArgParam(param,defval=""):
    for i in range(0, len(sys.argv)):
        if sys.argv[i] == param:
           return True

    return defval

def findArgParam(param):
    for i in range(0, len(sys.argv)):
        if sys.argv[i] == param:
           return i

    return -1
