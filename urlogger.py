# -*- coding: utf-8 -*-
"""
A class-interface to the Python logging module. If this class is
used, there is no need to 'import logging' in the program that
does the logging.
"""
import typing
from   typing import *

min_py = (3, 8)

###
# Standard imports, starting with os and sys
###
import os
import sys
if sys.version_info < min_py:
    print(f"This program requires Python {min_py[0]}.{min_py[1]}, or higher.")
    sys.exit(os.EX_SOFTWARE)

###
# Other standard distro imports
###
import argparse
import contextlib
import getpass
mynetid = getpass.getuser()
import logging
from   logging.handlers import RotatingFileHandler
import multiprocessing
import pathlib

###
# From hpclib
###
import linuxutils
from   urdecorators import trap

###
# imports and objects that are a part of this project
###
logger_daemon_name = 'urloggerd'
verbose = False

###
# Credits
###
__author__ = "George Flanagin"
__copyright__ = 'Copyright 2023'
__credits__ = "Ivan Sokolovskii ivan3177@github"
__version__ = 0.1
__maintainer__ = ['George Flanagin', 'Alina Enikeeva']
__email__ = ['hpc@richmond.edu']
__status__ = 'in progress'
__license__ = 'MIT'

class URLogger: pass

class URLogger:
    __slots__ = {
        'lock': 'A multiprocessing.Lock object',
        'directory': 'directory with the log files',
        'logfile': 'the logfile associated with this object',
        'formatter': 'format string for the logging records.', 
        'level': 'level of the logging object',
        'rotator': 'using the built-in log rotation system',
        'thelogger': 'the logging object this class wraps'
        }

    __values__ = (
        None,
        '/var/log/URLogger', 
        '/var/log/URLogger/log.log', 
        logging.Formatter('#%(levelname)-8s [%(asctime)s] (%(process)d) %(module)s: %(message)s'),
        False,
        logging.WARNING,
        None,
        None)

    __defaults__ = dict(zip(__slots__.keys(), __values__))


    @staticmethod
    def manufacture_lock() -> multiprocessing.RLock:
        return multiprocessing.RLock()


    def __init__(self, lock:multiprocessing.RLock, **kwargs) -> None:

        # Set the defaults.
        for k, v in URLogger.__defaults__.items():
            setattr(self, k, v)

        # Override the defaults if needed.
        for k, v in kwargs.items(): 
            if k in URLogger.__slots__:
                setattr(self, k, v)

        # Initialize the lock.
        if isinstance(lock, multiprocessing.synchronize.RLock):
            self.lock = lock
        else:
            raise Exception(f"wrong type of lock: {lock}")
        
        try:
            os.makedirs(self.directory, mode=0o755, exist_ok=True)
        except PermissionError as e:
            sys.stderr.write(f"Cannot access {self.directory}\n")
            raise e from None

        # log warnings to warning log file. 
        try:
            pathlib.Path(self.logfile).touch(mode=0o644, exist_ok=True)
            self.rotator = RotatingFileHandler(self.logfile, maxBytes=1<<24, backupCount=2)
        except Exception as e:
            sys.stderr.write(f"Unable to create or open {self.logfile}")
            raise e from None
            
        self.level = logging._nameToLevel[self.level] if isinstance(self.level, str) else int(self.level)
        self.rotator.setLevel(self.level)
        self.rotator.setFormatter(self.formatter)

        # setting up logger with handlers
        self.thelogger = logging.getLogger('URLogger')
        self.thelogger.setLevel(self.level)
        self.thelogger.addHandler(self.rotator)

    ###
    # These functions wrap the underlying logging activity, both
    # exposing the logger to the class object, and ensuring the
    # mutex operation.
    ###
    def debug(self, msg:str) -> object:
        with self.lock:
            self.thelogger.debug(msg)

    def info(self, msg:str) -> object:
        with self.lock:
            self.thelogger.info(msg)

    def warning(self, msg:str) -> object:
        with self.lock:
            self.thelogger.warning(msg)

    def error(self, msg:str) -> object:
        with self.lock:
            self.thelogger.error(msg)

    def critical(self, msg:str) -> object:
        with self.lock:
            self.thelogger.critical(msg)


    ###
    # Tinker with the object model a little bit.
    ###
    def __str__(self) -> str:
        """ return the name of the logfile. """
        return self.logfile


    def __int__(self) -> int:
        """ return the current level of logging. """
        return self.level if isinstance(self.level, int) else logging.getattr(self.level)


    def __call__(self, level:int) -> URLogger:
        """
        reset the level of logging, and return 'self' so that
        syntax like this is possible:

            mylogger(logging.INFO).info('a new message.')
        """
        self.level = logging._nameToLevel[level] if isinstance(level, str) else int(level)
        self.rotator.setLevel(self.level)
        self.thelogger.setLevel(self.level)
        return self 


if __name__ == '__main__':
    print("Create a logger.")
    lock = URLogger.manufacture_lock()
    logger = URLogger(lock, level=logging.DEBUG)
    print(f"{int(logger)=}")

    logger.info('This is purely informational') 
    logger.debug('This is a debug message.')
    logger.critical('This is *CRITICAL*')

    with open(str(logger)) as f:
        { print(_) for _ in f.readlines() }
    
