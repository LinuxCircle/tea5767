######!/usr/bin/python3 
######   # -*- coding: utf-8 -*-

import smbus as smbus 
import subprocess
import time
import sys

from Adafruit_I2C import Adafruit_I2C
import quick2wire.i2c as i2clib
from quick2wire.i2c import I2CMaster, writing_bytes, reading

attempt = 0
output=[]
bus = i2clib.I2CMaster()
add = 0x60 # I2C address circuit 
cof = 32768
i =  False
freq = 105.1
# Frequency distribution for two bytes (according to the data sheet) 
freq14bit = int (4 * (freq * 1000000 + 225000) / cof)
freqH = freq14bit >>8
freqL = freq14bit & 0xFF

data = [0 for i in range(4)]
                              # Descriptions of individual bits in a byte - viz.  catalog sheets 
add = 0x60 # I2C address circuit 
init = freqH&0x3F# freqH # 1.bajt (MUTE bit; Frequency H)  // MUTE is 0x80 disable mute and search mode & 0x3F

def backspace(n):
    # print((b'\x08' * n).decode(), end='') # use \x08 char to go back
    print('\r' * n, end='') 


i2c = smbus.SMBus(1) # newer version RASP (512 megabytes) 
#bus = smbus.SMBus (0) # RASP older version (256MB) 

def getFreq():
# getReady()
 frequency = 0.0
 results = bus.transaction(
  reading(add, 5)
 )

 frequency = ((results[0][0]&0x3F) << 8) + results[0][1];
 # Determine the current frequency using the same high side formula as above
 frequency = round(frequency * 32768 / 4 - 225000) / 1000000;
# print(frequency)
 return round(frequency,2)


def calculateFrequency():
 """calculate the station frequency based upon the upper and lower bits read from the device"""
#bus = smbus.SMBus (0) # RASP older version (256MB) 
 repeat = 0
 f =0.0
 with i2clib.I2CMaster() as b:
  results = b.transaction(
   reading(add, 5)
  )

 uF = results[0][0]&0x3F
 lF = results[0][1]
 # this is probably not the best way of doing this but I was having issues with the
 #       frequency being off by as much as 1.5 MHz
 current_freq = round((float(round(int(((int(uF)<<8)+int(lF))*cof/4-22500)/100000)/10)-.2)*10)/10
 return current_freq




#import pigpio

#i2c = smbus.SMBus(1) # newer version RASP (512 megabytes) 
#bus = smbus.SMBus (0) # RASP older version (256MB) 

#af = Adafruit_I2C(0x60, 1, True)
#pipi = pigpio.pi()



print("FM Radio Module TEA5767")

#script to get ready
#def getReady():
readyFlag = 0 
i = False
attempt = 0
results=[]
standbyFlag = 0
sys.stdout.flush()
time.sleep(0.1) 
print("Getting ready ", end ="")
while (i==False):
   #output = i2c.read_i2c_block_data(add,init)
   #i2c.read_byte(add)
   results = bus.transaction(
     reading(add, 5)
   )

   readyFlag = 1 if (results[0][0]&0x80)==128 else 0
   standbyFlag = 1 if (results[0][3]+0x40)!=319 else 0
   
   #print("result search mode:" , results[0][0]+0x40)
   #s = results[0][3]+0x40
   sys.stdout.flush()
   time.sleep(0.9)
   print(".", end = "")
#   print("Soft mute ", results[0][3]&0x08)
   #print(results[0][3]+0x40)
   i=standbyFlag*readyFlag
   attempt+=1
   if(attempt>10):
     break
if(i==True):
  print("Ready! (",attempt,")")
# print("Raw output ", results[0])
else:
  i2c.read_byte(add)
  print("Not ready!")


#current_address = i2c.read_byte(add) 
#time.sleep(1)
#getReady()
time.sleep(1)
print("Current frequency is " , getFreq(), "FM or ", calculateFrequency(),"FM")
#current_address = i2c.read_byte(add) 
#print("Current address " , current_address)

#writeFrequency(105.1)

def writeFrequency(f, mute):
 freq =  f # desired frequency in MHz (at 101.1 popular music station in Melbourne) 
 cof = 32768
 i=False
 attempt = 0
# Frequency distribution for two bytes (according to the data sheet) 
 freq14bit = int (4 * (freq * 1000000 + 225000) / cof)
 freqH = freq14bit >>8
 freqL = freq14bit & 0xFF

 data = [0 for i in range(4)]
                              # Descriptions of individual bits in a byte - viz.  catalog sheets 
 add = 0x60 # I2C address circuit
 if(mute==0): 
   init = freqH&0x3F# freqH # 1.bajt (MUTE bit; Frequency H)  // MUTE is 0x80 disable mute and search mode & 0x3F
 else:
   init = freqH&0x7F
 data[0] = freqL # 2.bajt (frequency L) 
 if(mute==0):
   data[1] = 0b10010000 # 3.bajt (SUD; SSL1, SSL2; HLSI, MS, MR, ML; SWP1) 
 else:
   data[1] = 0b00010110
 data[2] =  0b00010010 # 4.bajt (SWP2; STBY, BL; XTAL; smut; HCC, SNC, SI) 
 data[3] =  0b00000000 # 5.bajt (PLREFF; DTC; 0; 0; 0; 0; 0; 0) 

#data[1]=0xB0; #3 byte (0xB0): high side LO injection is on,.
#data[2]=0x10; #4 byte (0x10) : Xtal is 32.768 kHz
#data[3]=0x00; #5 byte0x00)

 while (i==False):
  try:
   i2c.write_i2c_block_data (add, init,data) # Setting a new frequency to the circuit 
  except IOError as e :
   #print("I/O error: {0}".format(e))
   i = False
   attempt +=1
   if attempt > 100000:
     break
  except Exception as e:
   print("I/O error: {0}".format(e))

  else:
   i = True
 print(attempt)
#  subprocess.call(['i2cdetect', '-y', '1'])
#  flag = 1     #optional flag to signal your code to resend or something

# if (i == False):
#  print("Took too long to change")
# else:
#  cf = calculateFrequency()  
#  gf = getFreq()
#  averageF =(cf+gf)/2
#  print("Frequency changed: ", cf , " " , gf, "(",attempt,")")

#writeFrequency(91.5)

i=False
f = getFreq()
fadd = 0
while (i==False):
   #output = i2c.read_i2c_block_data(add,init)
   #i2c.read_byte(add)
   fadd+=0.05
   f = (calculateFrequency()+getFreq())/2
   if(f<87 or f>108):
     f=87
   writeFrequency(f+fadd,1) 
   #print(f+fadd)
   time.sleep(0.1)
   results = bus.transaction(
     reading(add, 5)
   )
#   time.sleep(0.1)

   readyFlag = 1 if (results[0][0]&0x80)==128 else 0
   level = results[0][3]>>4
   print(results[0][0]&0x80 , " " , results[0][3]>>4)
   if(readyFlag and level>8):
     i=True
   else:
     i=False
   #print(results[0][0]&0x40)

writeFrequency((getFreq()+calculateFrequency())/2,0)
print("Frequency tuned: ", calculateFrequency(), "FM")

