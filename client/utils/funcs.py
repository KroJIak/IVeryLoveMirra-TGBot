from configparser import ConfigParser
import time
import sys

def getConfigObject(botConfigPath, commonPath=''):
    config = ConfigParser()
    config.read(commonPath + botConfigPath)
    return config

def changeWorkingPath(path):
    sys.path.insert(1, path)

def getPathAndFileName(fullPath):
    if not fullPath: return None, None
    path = fullPath.split('/')
    fileName = path.pop(-1)
    path = '/'.join(path) + '/'
    return path, fileName

def getLocalTime(format):
    localTime = time.localtime()
    match format:
        case 0: return time.strftime('%H:%M:%S', localTime)
        case 1: return time.strftime('%d-%m-%y-%H-%M-%S', localTime)

def getFullLocalTime():
    currentTime = getLocalTime(0)
    hour, minute, second = map(int, currentTime.split(':'))
    fullLocalTime = hour * 3600 + minute * 60 + second
    return fullLocalTime

def getLogFileName():
    localTime = getLocalTime(1)
    resultName = f'log-{localTime}.log'
    return resultName

def getDBWorkerObject(tableName, mainPath, commonPath, databasePath=None):
    path, fileName = getPathAndFileName(databasePath)
    changeWorkingPath(mainPath)
    from db.database import dbUsersWorker, dbAppealsWorker, dbLocalWorker
    match tableName:
        case 'users': resultDB = dbUsersWorker(mainPath + path, fileName)
        case 'appeals': resultDB = dbAppealsWorker(mainPath + path, fileName)
        case 'local': resultDB = dbLocalWorker()
        case _: resultDB = None
    changeWorkingPath(commonPath)
    return resultDB