from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import asyncio
from utils.funcs import *
from utils.const import ConstPlenty, UserInfo
from traceback import format_exc
import json
import logging
from random import shuffle
from threading import Thread
from time import time as gtime

# SETTINGS
const = ConstPlenty()
botConfig = getConfigObject('config/bot.ini', const.commonPath)
const.addConstFromConfig(botConfig)
logging.basicConfig(level=logging.INFO, filename=f'{const.commonPath}logs/{getLogFileName()}', filemode='w', format=const.logging.format)
dbUsers = getDBWorkerObject('users', const.mainPath, const.commonPath, databasePath=const.data.usersDatabasePath)
dbAppeals = getDBWorkerObject('appeals', const.mainPath, const.commonPath, databasePath=const.data.appealsDatabasePath)
dbLocal = getDBWorkerObject('local', const.mainPath, const.commonPath)
bot = Bot(const.telegram.token)
dp = Dispatcher()

def getTranslation(userId, key, inserts=[], lang=None):
    try:
        if not lang: lang = dbUsers.getFromUser(userId, 'lang')
        with open(f'{const.commonPath}lang/{lang}.json', encoding='utf-8') as langFile:
            langJson = json.load(langFile)
        text = langJson[key]
        if not inserts: return text
        for ins in inserts: text = text.replace('%{}%', str(ins), 1)
        return text
    except Exception:
        if dbUsers.isAdmin(userId): return getTranslation(userId, 'error.message', [format_exc()])
        else: return getTranslation(userId, 'error.message', ['wwc...'])

def getUserInfo(message):
    userInfo = UserInfo(message)
    if not dbUsers.isUserExists(userInfo.userId):
        permissions = dbUsers.getPermissions()
        lowestPermission = permissions['0']
        dbUsers.addNewUser(userInfo.userId, userInfo.username, userInfo.userFullName, const.data.defaultLang, lowestPermission)
    if not dbLocal.isUserExists(userInfo.userId):
        dbLocal.addNewUser(userInfo.userId)
    if str(userInfo.userId) == str(const.telegram.userId.mirra) and dbUsers.isUnregistered(userInfo.userId):
        dbUsers.setInUser(userInfo.userId, 'permission', 'guest')
    print(' | '.join(list(map(str, userInfo.getValues())) + [str(dbLocal.db[str(userInfo.userId)])]))
    return userInfo

def getChangeLangTranslation(userId):
    curLang = dbUsers.getFromUser(userId, 'lang')
    availableLangs = const.data.availableLangs
    nextIndexLang = (availableLangs.index(curLang) + 1) % len(availableLangs)
    curCountryFlag = getTranslation(userId, 'lang.countryflag')
    nextCountryFlag = getTranslation(userId, 'lang.countryflag', lang=availableLangs[nextIndexLang])
    resultTranslation = getTranslation(userId, 'button.changelang', [curCountryFlag, nextCountryFlag])
    return resultTranslation

def getMainKeyboard(userId):
    mainButtons = []
    mainButtons.append([types.KeyboardButton(text=getTranslation(userId, 'button.sad'))])
    mainButtons.append([types.KeyboardButton(text=getTranslation(userId, 'button.report'))])
    mainKeyboard = types.ReplyKeyboardMarkup(keyboard=mainButtons, resize_keyboard=True)
    return mainKeyboard

# COMMANDS
@dp.message(Command('start'))
async def startHandler(message: types.Message):
    userInfo = getUserInfo(message)
    if dbUsers.isUnregistered(userInfo.userId):
        await message.answer(getTranslation(userInfo.userId, 'permissions.cancel'), parse_mode='HTML')
        return
    dbLocal.setModeInUser(userInfo.userId, 0)
    stickers = dbAppeals.getStickers()
    mainKeyboard = getMainKeyboard(userInfo.userId)
    await message.answer(getTranslation(userInfo.userId, 'start.message', [userInfo.userFirstName]), reply_markup=mainKeyboard, parse_mode='HTML')
    await bot.send_sticker(userInfo.userId, stickers[0])

@dp.message(Command('sticker'))
async def stickerHandler(message: types.Message):
    userInfo = getUserInfo(message)
    if dbUsers.isUnregistered(userInfo.userId):
        await message.answer(getTranslation(userInfo.userId, 'permissions.cancel'), parse_mode='HTML')
        return
    stickers = dbAppeals.getStickers()
    shuffle(stickers)
    randomStiker = stickers[0]
    await bot.delete_message(userInfo.chatId, userInfo.messageId)
    await message.answer_sticker(sticker=randomStiker)

@dp.message(Command('send'))
async def sendHandler(message: types.Message):
    userInfo = getUserInfo(message)
    if dbUsers.isUnregistered(userInfo.userId):
        await message.answer(getTranslation(userInfo.userId, 'permissions.cancel'), parse_mode='HTML')
        return
    await bot.send_message(const.telegram.userId.mirra, ' '.join(userInfo.userText.split()[1:]))

def isSadCommand(userId, userText):
    return userText in ['/sad', f'/sad@{const.telegram.alias}', getTranslation(userId, 'button.sad')]

async def sadHandler(userInfo, message):
    for i in range(1, 5):
        await message.answer(getTranslation(userInfo.userId, f'sad.alarm.{i}'), parse_mode='HTML')
        await bot.send_message(const.telegram.userId.andrey, getTranslation(userInfo.userId, f'sad.alarm.andrey'), parse_mode='HTML')
        await asyncio.sleep(1)
    await sadThreadHandler()

async def sadThreadHandler():
    thread = Thread(target=sadThread)
    thread.start()

async def sadThread():
    lastTime = gtime()
    while lastTime + const.alarmDuration > gtime():
        if round(gtime() - lastTime, 2) % const.freqDuration == 0:
            await sendLovePack()
    mirraUserId = const.telegram.userId.mirra
    await bot.send_message(mirraUserId, getTranslation(mirraUserId, 'sad.success'), parse_mode='HTML')

async def sendLovePack():
    mirraUserId = const.telegram.userId.mirra
    compliments = dbAppeals.getCompliments()
    shuffle(compliments)
    randomCompliment = compliments[0]
    await bot.send_message(mirraUserId, getTranslation(mirraUserId, 'compliment.message', [randomCompliment]), parse_mode='HTML')
    stickers = dbAppeals.getStickers()
    shuffle(stickers)
    randomStiker = stickers[0]
    await bot.send_sticker(mirraUserId, sticker=randomStiker)

def isILoveYouPhrase(userText):
    text = ' '.join(userText.split())
    text = ''.join([word.lower() for word in text if 1040 <= ord(word) <= 1103 or word == ' '])
    return const.ILoveYou in text

async def ILoveYouHandler(userInfo, message):
    mainKeyboard = getMainKeyboard(userInfo.userId)
    stickers = dbAppeals.getStickers()
    shuffle(stickers)
    randomStiker = stickers[0]
    await message.answer(getTranslation(userInfo.userId, 'iloveyou.message'), reply_markup=mainKeyboard, parse_mode='HTML')
    await bot.send_sticker(userInfo.userId, randomStiker)

def isReportCommand(userId, userText):
    return userText in ['/report', f'/report@{const.telegram.alias}', getTranslation(userId, 'button.report')]

async def reportHandler(userInfo, message):
    dbLocal.setModeInUser(userInfo.userId, 1)
    await message.answer(getTranslation(userInfo.userId, 'report.message'), parse_mode='HTML')

async def sendReportHandler(userInfo, message):
    dbLocal.setModeInUser(userInfo.userId, 0)
    await message.answer(getTranslation(userInfo.userId, 'success.message'), parse_mode='HTML')
    await bot.send_message(const.telegram.userId.andrey, getTranslation(const.telegram.userId.andrey, 'report.send', [userInfo.userText]), parse_mode='HTML')

def isUnknownCommand(userText):
    return userText[0] == '/'

async def unknownCommandHandler(userInfo, message):
    mainKeyboard = getMainKeyboard(userInfo.userId)
    await message.answer(getTranslation(userInfo.userId, 'unknown.command.message'), reply_markup=mainKeyboard, parse_mode='HTML')

@dp.message()
async def mainHandler(message: types.Message):
    userInfo = getUserInfo(message)
    userMode = dbLocal.getModeFromUser(userInfo.userId)
    if dbUsers.isUnregistered(userInfo.userId):
        await message.answer(getTranslation(userInfo.userId, 'permissons.cancel'), parse_mode='HTML')
        return

    elif isSadCommand(userInfo.userId, userInfo.userText):
        await sadHandler(userInfo, message)
        return

    elif isReportCommand(userInfo.userId, userInfo.userText):
        await reportHandler(userInfo, message)
        return

    elif isUnknownCommand(userInfo.userText):
        await unknownCommandHandler(userInfo, message)
        return

    elif userMode > 0:
        match userMode:
            case 1: await sendReportHandler(userInfo, message)
        return

    elif isILoveYouPhrase(userInfo.userText):
        await ILoveYouHandler(userInfo, message)
        return

async def mainTelegram():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(mainTelegram())