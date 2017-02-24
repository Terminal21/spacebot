import cgi
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import os
import os.path
from threading import Thread
from ConfigParser import ConfigParser
from jabberbot import JabberBot, botcmd
from threading import Thread
import threading
from Queue import Empty, Queue
from exceptions import Exception
import logging
import time

def touch(fname):
    open(fname, 'a').close()
    os.utime(fname, None)


class SpaceApiHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        global spacebot
        print 'POST' 
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        status = form.getvalue('status')
        spacebot.spacebotstatus.update(status)        
        self.respond("""asdf""")

    def do_GET(self):
        self.respond("""geh weg""")

    def respond(self, response, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(response))
        self.end_headers()
        self.wfile.write(response)



class SpaceBot(JabberBot):

    PING_FREQUENCY = 60 # XMPP Ping every X seconds
    PING_TIMEOUT = 2 # Ping timeout

    def __init__(self, chatroom, *args, **kargs):
        logging.debug('SpaceBot initialized')
        super(SpaceBot, self).__init__(*args, **kargs)
        self.spacebotstatus = SpaceBotStatus(self)
        self.chatroom = chatroom
        self.messages = Queue()

    def idle_proc(self):
        try:
            message = self.messages.get_nowait()
        except Empty:
            return super(SpaceBot, self).idle_proc()
        logging.info('send message {} to chatroom {}'.format(
            message, self.chatroom))
        #self.send(self.chatroom, message, message_type='groupchat')
        self.broadcast(message)

    def serve_forever(self):
        self.conn = None
        self._JabberBot__finished = False
        super(SpaceBot, self).serve_forever()

    def say(self, message):
        self.messages.put(message)

    @botcmd
    def status(self, mess, args):
        """Status of the hackspace"""
        return "Der Space ist im Moment {}".format(
            "offen" if self.spacebotstatus.spaceopen else "zu")

    @botcmd
    def more(self, mess, args):
        """More about Terminal.21"""
        return """More infos @
                  web:\thttp://www.terminal21.de
                  mail:\tkontakt@terminal21.de
                  phone:\t+49 345 23909940
                  jabber muc:\tdiscuss@conference.terminal21.de"""




class SpaceBotStatus(object):
    current_status = 'closed'
    spaceopen = False

    def __init__(self, bot):
        self.listener = bot
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
        self.listener.say('Der Space ist jetzt {}'.format(
            'offen' if self.spaceopen else 'zu'))



def run():
    global spacebot
    logformat = "%(asctime)s %(levelname)s [%(name)s][%(threadName)s] %(message)s"
    logging.basicConfig(format=logformat, level=logging.DEBUG)

    config = ConfigParser()
    config.read('etc/spacebot.ini')

    username = config.get('spacebot', 'username')
    password = config.get('spacebot', 'password')
    chatroom = config.get('spacebot', 'chatroom')

    spacebot = SpaceBot(chatroom, username, password)
    server = HTTPServer(('', 8889), SpaceApiHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    while True:
        spacebot.serve_forever()
        time.sleep(20)
