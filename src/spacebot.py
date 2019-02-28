from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from ConfigParser import ConfigParser
from Queue import Empty, Queue
from exceptions import Exception
from threading import Thread
import cgi
import logging
import os
import os.path
import paho.mqtt.client as mqtt
import threading
import time


def touch(fname):
    open(fname, 'a').close()
    os.utime(fname, None)


class SpaceApiHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        global spacebotstatus
        print 'POST' 
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        status = form.getvalue('status')
        spacebotstatus.update(status)        
        self.respond("""asdf""")

    def do_GET(self):
        self.respond("""geh weg""")

    def respond(self, response, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(response))
        self.end_headers()
        self.wfile.write(response)



class SpaceBotStatus(object):
    current_status = 'closed'
    spaceopen = False

    def __init__(self, mqttc):
        self.mqttc = mqttc
        if os.path.isfile('spaceopen'):
            self.current_status = 'open'
            self.spaceopen = True

    def update(self, status):
        if status != self.current_status:
            if 'open' in status:
                self.spaceopen = True
                touch('spaceopen')
            else:
                self.spaceopen = False
                os.unlink('spaceopen')
            self.notify()
            self.current_status = status

    def notify(self):
        msg = 'true' if self.spaceopen else 'false'
        mqttc.connect('localhost')
        self.mqttc.publish('space/status/open', msg)
        mqttc.disconnect()


def run():
    global spacebotstatus
    logformat = "%(asctime)s %(levelname)s [%(name)s][%(threadName)s] %(message)s"
    logging.basicConfig(format=logformat, level=logging.DEBUG)

    config = ConfigParser()
    config.read('etc/spacebot.ini')

    mqttc = mqtt.Client()


    spacebotstatus = SpaceBotStatus(mqttc)
    server = HTTPServer(('', 8889), SpaceApiHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    while True:
        time.sleep(20)
