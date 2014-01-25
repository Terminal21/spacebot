from jabberbot import JabberBot, botcmd
from chatterbotapi import ChatterBotFactory, ChatterBotType

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
    username = 'horscht@terminal21.de'
    password = ''
    chatroom = 'discuss@conference.terminal21.de'

    factory = ChatterBotFactory()
    cbot = factory.create(ChatterBotType.CLEVERBOT)
    csession = cbot.create_session()

    bot = SpaceBot(csession, username, password)
    bot.join_room(chatroom)
    bot.serve_forever()
