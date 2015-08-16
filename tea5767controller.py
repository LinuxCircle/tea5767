#!/usr/bin/python3 
# -*- coding: utf-8 -*-

"""
Filename  	: tea5767controller.py
Programmer	: Dipto Pratyaksa for www.LinuxCircle.com
Date / Version	: August 2015. V1.0 
Tech		: Python 3, SMBUS, i2C, TEA5767 FM Radio, Raspberry Pi 2
Project		: Raspberry Pi Voice command robot via FM transmitter 
		  and receiver
Module		: TEA5767 Radio

Wish list	:
- Save strong stations into text file list

Reference	:
1. https://raw.githubusercontent.com/JTechEng/tea5767/
2. https://github.com/pcnate/fm-radio-python
3. http://www.astromik.org/raspi/38.htm

Usage		:
sudo python3 tea5767controller.py
or with executable file
sudo ./tea5767controller.py
"""



from tea5767stationscanner import tea5767

a = tea5767()
test =""

while(test!="x"):
  test=input("Radio command (u)p, (d)own, (t)est, e(x)it:")
  if(test=="u"):
    a.scan(1)
  elif(test=="d"):
    a.scan(0)
  elif(test=="t"):
    a.test()
  elif(test=="x"):
    a.off()
