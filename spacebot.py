from chatterbotapi import ChatterBotFactory, ChatterBotType
from ConfigParser import ConfigParser
from jabberbot import JabberBot, botcmd
import logging


class SpaceBot(JabberBot):

    def __init__(self, cleversession, *args, **kargs):
        self.cleverbot = cleversession
	super(SpaceBot, self).__init__(*args, **kargs)

    def unknown_command(self, mess, cmd, args):
        question = mess.getBody()
        question = question.encode("utf8")
	node = str(mess.getFrom()).split('/')[1]
	print node
	if (node=='horscht'):
            return None

        print question
        try:
            answ = self.cleverbot.think(question)
        except:
            return None
        print answ
        return answ

    @botcmd
    def status(self, mess, args):
        return "Hallo Welt, alles bestens!"


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    config = ConfigParser()
    config.read('etc/spacebot.ini')
    username = str(config.get('spacebot', 'username'))
    password = config.get('spacebot', 'password')
    chatroom = config.get('spacebot', 'chatroom')

    factory = ChatterBotFactory()
    cleverbot = factory.create(ChatterBotType.CLEVERBOT)
    cleversession = cleverbot.create_session()

    print dir(username)
    print dir(password)
    spacebot = SpaceBot(cleversession, username, password)
    spacebot.join_room(chatroom)
    spacebot.serve_forever()
