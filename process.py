"""
Process script feeds lines to the parser and saves the logs in an archive file
"""

from parser import *
from config import *
import time
import datetime
import json
import jsonpickle
import sys
import urllib2
import urllib

# IPv4 socket
import socket
origGetAddrInfo = socket.getaddrinfo

def getAddrInfoWrapper(host, port, family=0, socktype=0, proto=0, flags=0):
    return origGetAddrInfo(host, port, socket.AF_INET, socktype, proto, flags)

# replace the original socket.getaddrinfo by our version
socket.getaddrinfo = getAddrInfoWrapper

def push(name, data):
    """
    POST data to server
    """
    
    # encode data
    data = [(name, str(data))]
    data = urllib.urlencode(data)

    # send request
    req = urllib2.Request(url, data)
    req.add_header("Content-type", "application/x-www-form-urlencoded")

    page = urllib2.urlopen(req).read()

    print "Response: " + page



class Timer:
    
    def __init__(self):
        self.t = time.time()
    
    def mustSend(self, interval):
        '''
        Check if interval (in minutes) has elapsed
        '''
        if ( time.time() - self.t ) / 60 > interval :
            self.t = time.time()
            return True
        else:
            return False


if __name__ == "__main__":


    '''
    The following variables must be configured for your own setup:
    '''
    

    p = LogParser()
    t = Timer()

    try:
        line = ''
        linebuffer = []
        while True:
            time.sleep(0.01) # Sleep to avoid high CPU usage
            line += sys.stdin.read(1)
            
            if line.endswith('\n'):
                
                # if timestamped log, we need to remove the timestamp
                # timestamped log lines look like this:
                #     Feb 14 09:14:32 [88.163.143.89] MisterRick sprayed BrawBR
                if timestamp:
                
                    items = line.split()
                
                    if len(items) > 3:
                        items.pop(0)
                        items.pop(0)
                        items.pop(0)
                        
                    line = " ".join(items)
                
                # Parse line
                p.parseline(line)
                linebuffer.append(line)
                
                # Save line to archive
                #   lines are buffered to decrease I/O usage
                if len(linebuffer) > 10:
                    filename = str(datetime.date.today()) + ".log"
                    with open(filename, "a") as logfile:
                        for l in linebuffer:
                            logfile.write(l)
                
                    linebuffer = []
                    
                # Reset line
                line = ''
            
            # Check if need to upload data
            if t.mustSend(interval):
                jsonEncoded = json.dumps(json.loads(jsonpickle.encode(p, unpicklable=False)), indent=4)
                
                try:
                    push("stats", json)
                    print("Pushed Data to server: " + json.dumps(p.total))
                    
                    # Reset scores
                    p.reset()
                
                except urllib2.HTTPError as e:
                    print("Couldn't push to server: " + str(e))
                    
                print(jsonEncoded)
    
    except KeyboardInterrupt:
       sys.stdout.flush()
       pass

    jsonEncoded = json.dumps(json.loads(jsonpickle.encode(p, unpicklable=False)), indent=4)
    try:
        push("stats", json)
        print("Pushed Data to server: " + json.dumps(p.total))
        
        # Reset scores
        p.reset()
    
    except urllib2.HTTPError as e:
        print("Couldn't push to server: " + str(e))
        
    print(jsonEncoded)
    