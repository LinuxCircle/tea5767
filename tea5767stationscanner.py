#!/usr/bin/python3 
# -*- coding: utf-8 -*-

"""
Programmer: Dipto Pratyaksa for LinuxCircle.com
August 2015. Tech: Python 3, SMBUS, i2C, TEA5767 FM Radio, Raspberry Pi 2
Project:Raspberry Pi Voice command robot via FM transmitter and receiver 
Module: Tea 5767 Station Scanner
Future wish list:
- Save strong stations into text file list
Reference:
https://raw.githubusercontent.com/JTechEng/tea5767/
https://github.com/pcnate/fm-radio-python
http://www.astromik.org/raspi/38.htm
"""

import smbus as smbus 
import subprocess
import time
import sys

import websocket


import quick2wire.i2c as i2clib
from quick2wire.i2c import I2CMaster, writing_bytes, reading

cof = 32768 #crystal constant

def get_bit(byteval,idx):
    return ((byteval&(1<<idx))!=0);

class tea5767:
 def __init__(self):
   self.i2c = smbus.SMBus(1)
   self.bus = i2clib.I2CMaster()
   self.add = 0x60 # I2C address circuit 
   self.signal = 0
   self.chipID = self.getChipID()
   self.readyFlag = 0
   self.muteFlag = 0

   print("FM Radio Module TEA5767. Chip ID:", self.chipID)

   self.freq = self.calculateFrequency()                         
   if self.freq < 87.5 or self.freq > 107.9:
     self.freq = 101.9

   self.signal = self.getLevel()
   self.stereoFlag = self.getStereoFlag()
   print("Last frequency = " , self.freq, "FM. Signal level = ", self.signal, " " , self.stereoFlag)
   self.writeFrequency(self.freq, 1, 1)
#   self.preparesocket()
#   self.ws = None
 def prepareSocket(self):
   #time.sleep(1)   
   websocket.enableTrace(True)
   self.ws = websocket.create_connection("ws://192.168.1.2:8888/ws")
   self.ws.send('GET HTTP/1.1 200 OK\nContent-Type: text/html\n\n'.encode('utf-8'))
   print("Sending 'Hello, World'...")
   self.ws.send("Hello, World")
   print("Sent")
   print("Receiving...")
   result = self.ws.recv()
   print("Received '%s'" % result)
   self.ws.close()
 def on(self):
   self.writeFrequency(self.freq, 0, 0)

 def reset(self):
   #initiation
   if(not self.getReady()):
     print("resetting to default")
     self.i2c.write_byte(self.add, 0x00)
     self.getReady()


 def getFreq(self):
   frequency = 0.0
   results = self.bus.transaction(
     reading(self.add, 5)
   )

   frequency = ((results[0][0]&0x3F) << 8) + results[0][1];
   # Determine the current frequency using the same high side formula as above
   frequency = round(frequency * 32768 / 4 - 225000) / 1000000;
   return frequency
 
 def getLevel(self):
   level = 0
   results = self.bus.transaction(
     reading(self.add, 5)
   )
   level = results[0][3]>>4
   return level

 def getChipID(self):
   id = 0
   results = self.bus.transaction(
     reading(self.add, 5)
   )
   id = results[0][3]+0x0f

   return id

 def getStereoFlag(self):
   sf = 0
   results = self.bus.transaction(
     reading(self.add, 5)
   )
   sf = 1 if results[0][2]&0x80 else 0
   stereoflag = "stereo" if sf else "mono"
   return stereoflag

 def getTuned(self):
   results = self.bus.transaction(
     reading(self.add, 5)
   )
   elem=results[0][0]
   print("0 bits", int(get_bit(elem,0)), int(get_bit(elem,1)), int(get_bit(elem,2)), int(get_bit(elem,3)), int(get_bit(elem,4)), int(get_bit(elem,5)), int(get_bit(elem,6)),int(get_bit(elem,7)))

   elem=results[0][1]
   print("1 bits", int(get_bit(elem,0)), int(get_bit(elem,1)), int(get_bit(elem,2)), int(get_bit(elem,3)), int(get_bit(elem,4)), int(get_bit(elem,5)), int(get_bit(elem,6)),int(get_bit(elem,7)))

   elem=results[0][2]
   print("2 bits", int(get_bit(elem,0)), int(get_bit(elem,1)), int(get_bit(elem,2)), int(get_bit(elem,3)), int(get_bit(elem,4)), int(get_bit(elem,5)), int(get_bit(elem,6)),int(get_bit(elem,7)))

   elem=results[0][3]
   print("3 bits", int(get_bit(elem,0)), int(get_bit(elem,1)), int(get_bit(elem,2)), int(get_bit(elem,3)), int(get_bit(elem,4)), int(get_bit(elem,5)), int(get_bit(elem,6)), int(get_bit(elem,7)))




   return int(get_bit(elem,7))



 def calculateFrequency(self):
   """calculate the station frequency based upon the upper and lower bits read from the device"""
   repeat = 0
   f =0.0
   with i2clib.I2CMaster() as b:
     results = b.transaction(
       reading(self.add, 5)
     )

   uF = results[0][0]&0x3F
   lF = results[0][1]

   #good formula
   current_freq = round((float(round(int(((int(uF)<<8)+int(lF))*cof/4-22500)/100000)/10)-.2)*10)/10
   return current_freq



#script to get ready
 def getReady(self):

   readyFlag = 0 
   i = False
   attempt = 0
   results=[]
   standbyFlag = 0
   sys.stdout.flush()
   time.sleep(0.1) 
   print("Getting ready ", end ="")
   while (i==False):
     results = self.bus.transaction(
       reading(self.add, 5)
     )

     readyFlag = 1 if (results[0][0]&0x80)==128 else 0
     standbyFlag = 1 if (results[0][3]&0x40)!=319 else 0
   
     sys.stdout.flush()
     time.sleep(0.1)
     print(".", end = "")
     i=standbyFlag*readyFlag
     attempt+=1
     if(attempt>20):
       break
     time.sleep(0.2)
 
   if(i==True):
     print("Ready! (",attempt,")")
     return True
# print("Raw output ", results[0])
   else:
     self.i2c.read_byte(self.add)
     print("Not ready! (", attempt, ")")
     return False

 def writeFrequency(self,f, mute, direction):
   freq =  f # desired frequency in MHz (at 101.1 popular music station in Melbourne) 
   #cof = 32768
   i=False
   attempt = 0
   # Frequency distribution for two bytes (according to the data sheet) 
   freq14bit = int (4 * (freq * 1000000 + 225000) / cof)
   freqH = freq14bit >>8
   freqL = freq14bit & 0xFF

   self.muteFlag = mute

   data = [0 for i in range(4)]
   # Descriptions of individual bits in a byte - viz.  catalog sheets 
   if(mute==0): 
     init = freqH&0x3F# freqH # 1.byte (MUTE bit; Frequency H)  // MUTE is 0x80 disable mute and search mode & 0x3F
   elif(mute==1):
     init = freqH&0x7F #search mode
   elif(mute==2):
     init = freqH&0x80 #mute both channels
   data[0] = freqL # 2.byte (frequency L) 
   if(mute==0 and direction==1):
     data[1] = 0b10010000 # 3.byte (SUD; SSL1, SSL2; HLSI, MS, MR, ML; SWP1) 
   elif(mute==0 and direction==0):
     data[1] = 0b00010000
   else:
     data[1] = 0b00011110 #mute L & R during scanning
   if(mute==0):
     data[2] = 0b00010000 # 4.byte (SWP2; STBY, BL; XTAL; smut; HCC, SNC, SI) 
   else:
     data[2] = 0b00011111
   data[3] =  0b00000000 # 5.byte (PLREFF; DTC; 0; 0; 0; 0; 0; 0) 

#data[1]=0xB0; #3 byte (0xB0): high side LO injection is on,.
#data[2]=0x10; #4 byte (0x10) : Xtal is 32.768 kHz
#data[3]=0x00; #5 byte0x00)

   while (i==False):
     try:
       self.i2c.write_i2c_block_data (self.add, init, data) # Setting a new frequency to the circuit 
     except IOError as e :
       i = False
       attempt +=1
       self.reset() #error prevention
       if attempt > 100000:
         break
     except Exception as e:
       print("I/O error: {0}".format(e))
       self.reset()
     else:
       i = True


 def scan(self,direction):
   i=False
   fadd = 0
   softMute = 0
   while (i==False):
     if(direction==1):
       fadd=0.1
     else:
       fadd=-0.1
     #get current frequency, more accurately by averaging 2 method results
     self.freq = round((self.calculateFrequency()+self.getFreq())/2,2)
     if(self.freq<87.5):
       self.freq=108
     elif(self.freq>107.9):
       self.freq=87.5
     self.writeFrequency(self.freq+fadd,1,direction)

     #give time to finish writing, and then read status
     time.sleep(0.03)
     results = self.bus.transaction(
       reading(self.add, 5)
     )
     self.freq = round((self.calculateFrequency()+self.getFreq())/2,2) #read again

     softMute = results[0][3]&0x08
     standbyFlag = 0 if results[0][3]&0x40 else 1
     self.signal = results[0][3]>>4
     self.stereoFlag = self.getStereoFlag()
     self.IFcounter = results[0][2]&0x7F
     self.readyFlag = 1 if results[0][3]&0x80 else 0
 

     f = open('telek.txt', 'w')
     f.write(str(self.freq)+"\n")
#     self.ws.send(self.freq)
 #    self.serversocket.sendall(str(self.freq).encode('UTF-8'))
     print("Before tuning", self.getTuned())
     #tune into station that has strong signal only
     if(self.readyFlag):
       print("Frequency tuned:",self.freq , "FM (Strong",self.stereoFlag,"signal:",self.signal,")")
     else:
       print("Station skipped:",self.freq , "FM (Weak",self.stereoFlag,"signal:",self.signal,")")
     i=self.readyFlag
   self.writeFrequency(self.freq ,0,direction)

   self.readyFlag = self.getTuned()
   print("After tuning:", self.readyFlag)

 def off(self):
   print("Radio off")
   self.writeFrequency(self.calculateFrequency(), 2,0) 
   #a = self.getMute()
   a = self.getTuned()
   print("Radio off",a)
   return ("radio off")

 def mute(self):
   if(self.muteFlag):
     self.writeFrequency(self.calculateFrequency(), 0,0)
     print("unmute")
   else:
     self.writeFrequency(self.calculateFrequency(), 1,0)
     print("mute")
   return ("radio muted")


 def test(self):
   print("Testing mode")
   print("Scanning up...")
   self.scan(1)
   print("Listening for 10 seconds")
   time.sleep(10)
   print("Scanning down...")
   self.scan(0)
   print("Listening for 10 seconds")
   time.sleep(10)
   print("done")
  
 def info(self):
   data ={}
   data['freq'] = str(self.freq)
   data['level'] = self.signal
   data['stereo'] = str(self.stereoFlag)
   data['tuned'] = self.readyFlag
   data['mute'] = self.muteFlag

   print(data)
   return data  
#sample usage below:
#radio = tea5767()
#radio.scan(1)
#time.sleep(15)
#radio.scan(1)
#time.sleep(15)
#radio.scan(0)
#time.sleep(15)
#radio.scan(0)
#time.sleep(15)
#radio.off()

