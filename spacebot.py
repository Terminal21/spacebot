from chatterbotapi import ChatterBotFactory, ChatterBotType
from ConfigParser import ConfigParser
from jabberbot import JabberBot, botcmd
from threading import Thread
from Queue import Empty, Queue
import logging
import zmq


class SpaceBot(JabberBot):

    def __init__(self, publisher, chatroom, *args, **kargs):
        logging.debug('SpaceBot initialized')
	super(SpaceBot, self).__init__(*args, **kargs)

	self.chatroom = chatroom
        self.join_room(self.chatroom)

        factory = ChatterBotFactory()
        cleverbot = factory.create(ChatterBotType.CLEVERBOT)
        self.cleversession = cleverbot.create_session()

        self.messages = Queue()

        self.spacemrecvr = SpaceMessageRecvr(self, publisher)
        self.spacemrecvr.start()

    def idle_proc(self):
        try:
            message = self.messages.get_nowait()
        except Empty:
            return super(SpaceBot, self).idle_proc()
        logging.info('send message {} to chatroom {}'.format(
            message, self.chatroom))
        self.send(self.chatroom, message, message_type='groupchat')

    def say(self, message):
        self.messages.put(message)

    def shutdown(self):
        self.spacemrecvr.stop()
        self.spacemrecvr.join()
        super(SpaceBot, self).shutdown()

    def unknown_command(self, mess, cmd, args):
        question = mess.getBody()
        question = question.encode("utf8")
	node = str(mess.getFrom()).split('/')[1]
	if (node=='horscht'):
            return None

        try:
            answ = self.cleversession.think(question)
        except:
            return None
        return answ

    @botcmd
    def status(self, mess, args):
        return "Hallo Welt, alles bestens!"


class SpaceMessageRecvr(Thread):

    def __init__(self, spacebot, publisher):
        Thread.__init__(self) 

        logging.debug('SpaceMessageRecvr initialized')
        self.spacebot = spacebot

        zcontext = zmq.Context()
        self.subscriber = zcontext.socket(zmq.SUB)
        self.subscriber.connect(publisher)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, '')

    def run(self):
        logging.info('starting zmq subscription')
        while True:
            message = self.subscriber.recv()
            logging.info('receving zmq message {}'.format(str(message)))
            self.spacebot.say(message)

    def stop(self):
        logging.info('stopping zmq subscription')
        self.subscriber.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    config = ConfigParser()
    config.read('etc/spacebot.ini')
    username = config.get('spacebot', 'username')
    password = config.get('spacebot', 'password')
    chatroom = config.get('spacebot', 'chatroom')
    publisher = config.get('zmq', 'publisher')

    spacebot = SpaceBot(publisher, chatroom, username, password)
    spacebot.serve_forever()
