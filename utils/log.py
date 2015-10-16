import logging
from logging.handlers import TimedRotatingFileHandler

from utils.patterns.singleton import Singleton


class Logger(object):

    __instance = None

    # Remember do not directly use __init__(); use get_instance() method instead
    def __init__(self):
        self._logger = logging.getLogger("FrameworkLogger")
        self._logger.setLevel(logging.DEBUG)

        # Handlers
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        fh = TimedRotatingFileHandler(filename='log/framework.log', when='midnight', interval=1, encoding='UTF-8')
        fh.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s: %(levelname)s \t %(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        self._logger.addHandler(ch)
        self._logger.addHandler(fh)

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = Logger()
        return cls.__instance

    def __repr__(self):
        return "Logger[%s]" % self._logger.name

    def info(self, logger, msg, *args, **kwargs):
        self._logger.info(logger + ' says: ' + msg, *args, **kwargs)

    def warning(self, logger, msg, *args, **kwargs):
        self._logger.warning(logger + ' says: ' + msg, *args, **kwargs)

    def debug(self, logger, msg, *args, **kwargs):
        self._logger.debug(logger + ' says: ' + msg, *args, **kwargs)

    def error(self, logger, msg, *args, **kwargs):
        self._logger.error(logger + ' says: ' + msg, *args, **kwargs)
