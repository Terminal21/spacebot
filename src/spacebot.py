#from chatterbotapi import ChatterBotFactory, ChatterBotType
from ConfigParser import ConfigParser
from jabberbot import JabberBot, botcmd
from threading import Thread
from Queue import Empty, Queue
from exceptions import Exception
import logging
import zmq


class SpaceBot(JabberBot):

    def __init__(self, chatroom, *args, **kargs):
        logging.debug('SpaceBot initialized')
        super(SpaceBot, self).__init__(*args, **kargs)

        self.chatroom = chatroom
#        self.join_room(self.chatroom)

#        factory = ChatterBotFactory()
#        cleverbot = factory.create(ChatterBotType.CLEVERBOT)
#        self.cleversession = cleverbot.create_session()

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

    def say(self, message):
        self.messages.put(message)

#    def unknown_command(self, mess, cmd, args):
#        question = mess.getBody()
#        question = question.encode("utf8")
#        node = str(mess.getFrom()).split('/')[1]
#        if (node=='horscht'):
#                return None
#
#        try:
#            answ = self.cleversession.think(question)
#        except:
#            return None
#        return answ

    @botcmd
    def status(self, mess, args):
        """Status of the hackspace"""
        return "Der Space ist im Moment {}".format(
            "offen" if self.status.spaceopen else "zu")

    @botcmd
    def more(self, mess, args):
        """More about Terminal.21"""
        return """More infos @
                  web:\thttp://www.terminal21.de
                  mail:\tkontakt@terminal21.de
                  phone:\t+49 345 23909940
                  jabber muc:\tdiscuss@conference.terminal21.de"""


class SpaceMessage(object):

    def __init__(self, spaceopen = None):
        self.spaceopen = spaceopen


class SpaceStatus(object):

    def __init__(self, listener):
        self.listener = listener
        self.spacemrecvr = SpaceMessageRecvr(self)
        self.spacemrecvr.start()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.spacemrecvr.stop()

    def update(self, spacemessage):
        pass


class SpaceBotStatus(SpaceStatus):
    spaceopen = False
    changed = False

    def update(self, spacemessage):
        if 'spaceopen' in spacemessage:
            spacemessage['spaceopen'] = bool(spacemessage['spaceopen'])
            if not self.spaceopen == spacemessage['spaceopen']:
                self.spaceopen = spacemessage['spaceopen']
                logging.info('SpaceBotStatus spaceopen changed to {}'.format(
                    self.spaceopen))
                self.changed = True

        if self.changed:
            self.notify()
            self.changed = False

    def notify(self):
        self.listener.say('Der Space ist jetzt {}'.format(
            'offen' if self.spaceopen else 'zu'))



class SpaceMessageRecvr(Thread):

    _continue = True

    def __init__(self, listener):
        Thread.__init__(self) 
        self.daemon = True

        config = ConfigParser()
        config.read('etc/spacebot.ini')
        publisher = config.get('zeromq', 'publisher')

        logging.debug('SpaceMessageRecvr initialized')
        self.listener = listener

        zcontext = zmq.Context()
        self.subscriber = zcontext.socket(zmq.SUB)
        self.subscriber.connect(publisher)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, '')

    def run(self):
        logging.info('starting zeromq subscription')
        while self._continue:
            try:
                message = self.subscriber.recv_json()
                logging.info('receving zeromq message {}'.format(str(message)))
                self.listener.update(message)
            except Exception as e:
                logging.error(e)

    def stop(self):
        self.__continue = False
        self.subscriber.close()
        logging.info('stopping zeromq subscription')


#if __name__ == '__main__':
def run():
    logging.basicConfig(level=logging.DEBUG)

    config = ConfigParser()
    config.read('etc/spacebot.ini')
    username = config.get('spacebot', 'username')
    password = config.get('spacebot', 'password')
    chatroom = config.get('spacebot', 'chatroom')

    spacebot = SpaceBot(chatroom, username, password)
    with SpaceBotStatus(spacebot) as spacestatus:
        spacebot.status = spacestatus
        spacebot.serve_forever()
