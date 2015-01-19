import socket
import re
import threading
import time
import subprocess
import base64
import os
import sys
from pylab import *
results=[]
timelts=[]
resstr=[]
timeltsf=[]

site=raw_input("Site: ")
interval=float(raw_input("Interval: "))
port=int(raw_input("Web Port: "))
amt=int(raw_input("View Amount: "))
refresh=float(raw_input("Refresh Speed: "))
UI=""
count=0
#UI=raw_input("Type a command or quit to exit:")
def plotter(x,y):
  plot(x, y)
  xlabel('time (s)')
  ylabel('latency (ms)')
  title('Ping results for:' +site)
  grid(True)
  savefig("Results.png")
  clf()
  

class Logicer(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
  def run(self):
    p = subprocess.Popen(['ping','-i',str(interval), site],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    mod=0
    for line in iter(p.stdout.readline, b''):
      if(len(line.split(" ms"))>1):
        pres=line.rpartition('=')[-1].split(" ms")[0]
        count=len(timelts)
        results.append(float(pres))
        resstr.append(str(pres))
        timelts.append(float(count))
        if len(timelts)>amt:
          timelts.pop()

        if len(results)>amt:
          resstr.pop(0)
          results.pop(0)
        plotter(timelts,results)

logic= Logicer()
logic.setDaemon(True)
logic.start()

crap="""
<script type="text/javascript" >
timeout="""+str(refresh*1000)+""";
refresh=100;
count=timeout;
function update() {
setTimeout(function () {
count=count-refresh;
if (count<0) {count=timeout;document.location=document.location;}
update();
},refresh);	
}
update();
</script>
</html> 
"""


# Standard socket stuff:
host = '0.0.0.0'  # do we need socket.gethostname() ?
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))
sock.listen(1)  # don't queue up any requests
 
# Loop forever, listening for requests:
while True:
    if not logic.is_alive() :
      logic= Logicer()
      logic.setDaemon(True)
      logic.start()
      print ("Once upon a time... "+str(len(results))+", died.")
    csock, caddr = sock.accept()
    print "Connection from: " + `caddr`
    req = csock.recv(1024)  # get the request, 1kB max
    #print req
    match=1
    if match:
        f=open("Results.png","rb")
        csock.sendall("HTTP/1.0 200 OK \n  Content-Type: image/png \n\n"+ "<html><img src='data:image/gif;base64,"+base64.b64encode(f.read())+"'>"+crap)
        f.close
    else:
        # If there was no recognised command then return a 404 (page not found)
        print "Returning 404"
        csock.sendall("HTTP/1.0 404 Not Found\r\n")
    csock.close()
