# -*- coding: utf-8 -*-

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
    
def get_int_val(str_val):
    if str_val == "" or str_val == None: 
       return 0
    return int(str_val)

def get_str_val(str_val):
    if str_val == None: 
       return ""
    return str_val
