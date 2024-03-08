
class configCategoryObject():
    def __init__(self, config, nameCategory):
        self.config = config
        self.nameCategory = nameCategory

    def get(self, elm):
        return self.config.get(self.nameCategory, elm)

class UserIdTelegram():
    def __init__(self, mirra, andrey):
        self.mirra = mirra
        self.andrey = andrey

class Telegram(configCategoryObject):
    def __init__(self, config):
        super().__init__(config, 'Telegram')
        self.token = self.get('token')
        self.alias = self.get('alias')
        self.userId = UserIdTelegram(self.get('mirraUserId'),
                                     self.get('andreyUserId'))

class GPT(configCategoryObject):
    def __init__(self, config):
        super().__init__(config, 'GPT')
        self.api = self.get('api')
        self.systemPrompt = self.get('systemPrompt')
        self.model = self.get('model')

class Data(configCategoryObject):
    def __init__(self, config):
        super().__init__(config, 'Data')
        self.usersDatabasePath = self.get('usersDatabasePath')
        self.appealsDatabasePath = self.get('appealsDatabasePath')
        self.availableLangs = self.get('availableLangs')
        self.availableLangs = self.availableLangs.split(', ')
        self.defaultLang = self.get('defaultLang')
        self.secretKey = self.get('secretKey')

class Logging():
    def __init__(self):
        self.format = '%(asctime)s %(levelname)s %(message)s'

class ConstPlenty():
    def __init__(self, config=None):
        if config: self.addConstFromConfig(config)
        self.commonPath = '/'.join(__file__.split('/')[:-2]) + '/'
        self.mainPath = '/'.join(__file__.split('/')[:-3]) + '/'
        self.logging = Logging()
        self.alarmDuration = 3 * 60
        self.freqDuration = 10
        self.freqNotify = 2.5 * 60 * 60
        self.ILoveYou = 'люблю тебя'

    def addConstFromConfig(self, config):
        self.telegram = Telegram(config)
        self.gpt = GPT(config)
        self.data = Data(config)

class UserInfo():
    def __init__(self, message):
        self.chatId = message.chat.id
        self.userId = message.from_user.id
        self.username = message.from_user.username
        self.userFirstName = message.from_user.first_name
        self.userFullName = message.from_user.full_name
        self.messageId = message.message_id
        self.userText = message.text

    def getValues(self):
        values = [self.chatId, self.userId, self.username, self.userFirstName, self.userFullName, self.messageId, self.userText]
        return values
