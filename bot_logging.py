from loguru import logger
from sys import stdout
from configparser import ConfigParser

logger.remove() # remove the default logger

config = ConfigParser()
config.read('config.ini')
consoleLevel = config["LOGGING"].get("consoleLevel", "INFO")
fileLevel = config["LOGGING"].get("fileLevel", "INFO")


fmt = "{time: YYYY-MM-DD HH:mm:ss:SSZZ} | {level: <8} | {name}:{function}:{line} | {message}"
logger.add("bot.log", retention="30 days", level=fileLevel, format=fmt, backtrace=True, diagnose=True)


fmt2 = "{time: YYYY-MM-DD HH:mm:ss:SSZZ} | {level: <8} | {message}"
logger.add(stdout, format=fmt2,level=consoleLevel)
