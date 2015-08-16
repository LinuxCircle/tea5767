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
