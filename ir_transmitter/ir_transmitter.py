import ujson
import utime
import micropython
micropython.alloc_emergency_exception_buf(100)
# how to use:
#   from irSelectCMD import *
#   irCMDList = irSelectCMD(0)

def irSelectCMD(ctrlNum, txtAddr="ir_transmitter/irLists.txt"):
  
        with open(txtAddr, "r", encoding="utf-8") as txt:
            ir_data = ujson.load(txt)
            if str(ctrlNum) in ir_data:
                return ir_data[str(ctrlNum)]
            else:
                return None
   

def irSendCMD(pwmObject, ctrlList, duty=360):

    pwmObject.deinit()
    pwmObject.init()
    pwmObject.freq(38000)
    pwmObject.duty(0)
    utime.sleep_ms(100)

    ctrlListLen = len(ctrlList)

    for i in range(ctrlListLen):
        if i % 2 == 0:
            pwmObject.duty(duty)
        else:
            pwmObject.duty(0)
        utime.sleep_us(ctrlList[i])

    pwmObject.duty(0)

    utime.sleep_ms(100)