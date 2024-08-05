import machine
from ir_transmitter.ir_transmitter import irSelectCMD, irSendCMD
import remote
import gc
import utime
from machine import I2C, Pin
import adafruit_mlx90640
import network
import ntptime
import ufirebase
from fastapi import FastAPI

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Hello World"}
def callback(data, addr, ctrl):
    print('Data {0} Addr {1} Ctrl {2}'.format(data, addr, ctrl))
    
    if data == 69:
        irLedPwmObject = machine.PWM(machine.Pin(17, machine.Pin.OUT), freq=38000, duty=0)
        irCMDList = irSelectCMD(0)
        irSendCMD(irLedPwmObject, irCMDList, duty=360)
        print(irCMDList)
    if data == 70:
        irLedPwmObject = machine.PWM(machine.Pin(17, machine.Pin.OUT), freq=38000, duty=0)
        irCMDList = irSelectCMD(1)
        irSendCMD(irLedPwmObject, irCMDList, duty=360)
        print(irCMDList)


ir = remote.NEC_16(machine.Pin(35, machine.Pin.IN), callback)


# Function Get Current Time from NTP Server
def get_current_time():
    actual_time = utime.localtime(utime.time() + 25200)
    rtc = machine.RTC()
    rtc.datetime((actual_time[0], actual_time[1], actual_time[2], 0, actual_time[3], actual_time[4], actual_time[5], 0))
    t = rtc.datetime()
    return '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(t[0], t[1], t[2], t[4], t[5], t[6])


# Function Send Data to Firebase
def data_to_firebase(currentTime, message):
    try:
        path = "TEST/" + currentTime + "/"
        ufirebase.put(path, message)
    except Exception as e:
        print(e)
        machine.reset()


# Set CPU Frequency
machine.freq(240000000)

# Adafruit MLX90640
i2c = I2C(0, scl=Pin(22, Pin.OUT), sda=Pin(21, Pin.OUT), freq=800000)
mlx = adafruit_mlx90640.MLX90640(i2c)
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

# Setting Wi-Fi
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Booklab', 'ccsadmin')  
while not sta_if.isconnected():
    pass

# URL of your Firebase Realtime Database
ufirebase.setURL('https://data-esp32-718d0-default-rtdb.firebaseio.com/')

while True:
    try:
        gc.collect()
        ntptime.settime()
        frame = [0] * 768
        mlx.getFrame(frame)
        message = ",".join(map(str, frame))
        data_to_firebase(get_current_time(), message)
        utime.sleep(5)

    except Exception as e:
        print(e)
        machine.reset()

    finally:
        gc.collect()
        frame = []


# from ir_receiver import irGetCMD

# irGetCMD(35)