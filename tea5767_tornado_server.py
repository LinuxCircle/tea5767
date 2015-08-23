import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

import tea5767stationscanner


class IndexHandler(tornado.web.RequestHandler):
 @tornado.web.asynchronous
 def get(self):
  self.render("tea5767_tornado.html")

class WSHandler(tornado.websocket.WebSocketHandler):

 controller = None
 def check_origin(self, origin):
  return True

 def open(self):
  print ("connecting...")
  try:
   #self.controller = DeviceController()
   #self.write_message("Hello world!")
   self.controller=tea5767stationscanner.tea5767()
   self.controller.on()
   data=self.controller.info()
   self.write_message(data)
#   self.controller.prepareSocket()
  except Exception as a:
   print(a)

 def on_message(self, message):
  print("Command:", message)
  data=""
  try:

   if(message=="up"):
    self.controller.scan(1)
   elif(message=="down"):
    self.controller.scan(0)
   elif(message=="off"):
    data=self.controller.off()
   elif(message=="mute"):
    data=self.controller.mute()
   data=self.controller.info()
   
   if(message=="off"):
    data=self.controller.off()
    
   self.write_message(data)
  except Exception as a:
   print("Error: ", a)

 def on_close(self):
  print ("closing sockets")
  self.controller =""


static_path = "/home/pi/Projects/tea5767/"
favicon_path =""

application = tornado.web.Application([
 (r'/favicon.ico', tornado.web.StaticFileHandler, {'path': favicon_path}),
 (r"/images/(.*)",tornado.web.StaticFileHandler, {"path": "./images"},),
 (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),
 (r'/', IndexHandler),
 (r"/ws", WSHandler),
])


if __name__ == "__main__":
 http_server = tornado.httpserver.HTTPServer(application)
 print ("Waiting client connection via browser port 8888")
 http_server.listen(8888)
 tornado.ioloop.IOLoop.instance().start()
