# -*- coding: utf-8 -*-

###
# Credits
###
__author__ = 'George Flanagin & Alina Enikeeva'
__copyright__ = 'Copyright 2023'
__credits__ = None
__version__ = 0.1
__maintainer__ = 'George Flanagin & Alina Enikeeva'
__email__ = ['hpc@richmond.edu']
__status__ = 'pre-production'
__license__ = 'MIT'

import typing
from   typing import *

min_py = (3, 8)

###
# Standard imports, starting with os and sys. Check compatibility.
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
import configparser
import contextlib
import getpass
import signal
import time
import re
import sqlite3
from sqlitedb import SQLiteDB
from datetime import datetime
mynetid = getpass.getuser()

#
###
# From hpclib
###
from   dorunrun import dorunrun
import fifo
import fileutils
from fileutils import read_whitespace_file
import linuxutils
import sloppytree
import slurmutils
from   urdecorators import trap
from urlogger import URLogger
###
# imports and objects that are a part of this project
###

###
# Globals
###
caught_signals = [  
    signal.SIGINT, 
    signal.SIGQUIT, 
    signal.SIGHUP, 
    signal.SIGTERM,
    signal.SIGUSR1, 
    signal.SIGUSR2 
    ]


my_cwd = os.getcwd()
myargs = None
mynetid = getpass.getuser()
verbose = False
db = None
mylock = URLogger.manufacture_lock()

@trap
def handler(signum:int, stack:object=None) -> None:
    """
    Universal signal handler.
    """
    global myargs
    mylogger = URLogger(mylock, level = myargs.verbose)
    #mylogger = URLogger(mylock, myargs.verbose)
    if signum in {signal.SIGHUP, signal.SIGUSR1}:
        mylogger.debug('Reopening logging files')
        dynamically_installed_main(myargs)

    elif signum in {signal.SIGUSR2, signal.SIGQUIT, signal.SIGTERM, signal.SIGINT}:
        mylogger.debug('Closing up.')
        fileutils.fclose_all()
        sys.exit(os.EX_OK)

    elif signum in {signal.SIGCHLD}:
        return

    else:
        mylogger.debug(f"ignoring signal {signum}. Check list of handled signals.")

@trap
def dynamically_installed_events() -> int:
    """
    This is the event loop.
    """
    global myargs, mylogger

    found_stop_event = False

    while not found_stop_event:
        # Wait a day for someone to submit .. something.
        time.sleep(60*60*24)
    fileutils.fclose_all()
    mylogger.info('All files closed') 
    return os.EX_OK


@trap
def execute_sql(sqlfile: object) -> None:
    """Executes a file with SQL script"""
    return
    file = open(sqlfile, "r")
    sql = file.read()
    file.close()

    commands = sql.split(";")
    for command in commands:
        db.execute_SQL(command) 

@trap
def dynamically_installed_main(myargs:argparse.Namespace) -> int:
    """
    Do a little setup, and then start the program as a daemon.
    """
    global db
    global my_cwd
     
    mylogger = URLogger(mylock, level = myargs.verbose)

   
    mylogger.critical(f'The logging level is {int(mylogger)}')

    #create tables in a database 
    sqlfile = myargs.sqlscript
    execute_sql(sqlfile)

    #SQL statements to insert values into the table
    SQL_installed = """INSERT INTO installed (workstation, package_name) VALUES (?,?)"""
    SQL_otherdata =  """INSERT INTO otherdata (workstation, inquiry, result) VALUES (?,?,?)"""
    
    commands = {} 
    #read commands from a file and insert them into a dictionary
    with open(myargs.commands, "r") as commands_file:
        for line in commands_file.readlines():
            items = line.split(":")
            key, value = items[0], items[1].split("\n")[0] #get rid of the new line character in the value
            commands[key] = value
    #run commands for each workstation
    for just_name in read_whitespace_file(myargs.input):
        
        for key, command in commands.items():        
            
            # insert package name into table installed and everything else - into table otherdata     
            if key == "standard":
                packages = dorunrun(command.format(just_name), return_datatype = str)
                for package in packages.split("\n"):
                    #put in the contents of the result to the table
                    try:
                        db.execute_SQL(SQL_installed, just_name, package)
                    except sqlite3.Error:
                        pass
            else:
                result = dorunrun(command.format(just_name), return_datatype = str)
                if command == 'redhat_os': print(result)
                if len(result)==0: result = "None" #if command returns nothing, record None in the table
                try:
                    db.execute_SQL(SQL_otherdata, just_name, key, result)
                except sqlite3.Error:
                    pass
        db.commit() 
                  
    os.chdir(my_cwd) 

    not myargs.debug and linuxutils.daemonize_me()
    
    return dynamically_installed_events()


if __name__ == '__main__':

    this_dir=os.path.dirname(os.path.realpath(__file__))
    
    parser = argparse.ArgumentParser(prog="dynamically_installed", 
        description="What dynamically_installed does, dynamically_installed does best.")
    parser.add_argument('-d', '--debug', action='store_true', 
        help="Run program interactively for debugging purposes.")
    parser.add_argument('-o', '--output', type=str, default="",
        help="Name of the output (logging) file.")
    parser.add_argument('-v', '--verbose', type=str, 
        choices=('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'),
        default='ERROR',
        help="Be chatty or not at the corresponding log level.")

    parser.add_argument('-i', '--input', type=str, default=os.path.realpath(f"{this_dir}/mylistofhosts.txt"),
        help="Input file name that contains information about current workstations.")
    parser.add_argument('--commands', type=str, default=os.path.realpath(f"{this_dir}/commandsToInstall.txt"),
        help="Input file name that contains all the commands that we want to run to collect information about all the packages installed on workstations.")

    parser.add_argument('--db', type=str, default=os.path.realpath(f"{this_dir}/installed.db"),
        help="Input database name that contains information with packages installed on current workstations.")
    parser.add_argument('-sql', '--sqlscript', type=str, default=os.path.realpath(f"{this_dir}/installed.sql"),
        help="Input file name with sql script that creates the table, which stores workstations and packages installed on them.")
   
    myargs = parser.parse_args()
    verbose = myargs.verbose
 
    try:
        db = SQLiteDB(myargs.db)
    except:
        db = None
        print(f"Unable to open {myargs.db}")
        sys.exit(EX_CONFIG)
        
    ###
    # If we are running the program from the command line, then it
    # is useful to have ctrl-C interrupt the program. Same if we
    # logoff.
    ###
    if myargs.debug:
        caught_signals.remove(signal.SIGINT)
        caught_signals.remove(signal.SIGHUP)

    for _ in range(1,32):
        try:
            signal.signal(_, handler)
        except OSError as e:
            sys.stderr.write(f'cannot reassign signal {_}\n')
        else:
            # sys.stderr.write(f'signal {_} is being handled.\n')
            pass
    
    try:
        outfile = sys.stdout if not myargs.output else open(myargs.output, 'w')
        with contextlib.redirect_stderr(outfile):
            sys.exit(globals()[f"{os.path.basename(__file__)[:-3]}_main"](myargs))

    except Exception as e:
        print(f"Escaped or re-raised exception: {e}")

