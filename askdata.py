# -*- coding: utf-8 -*-
import typing
from   typing import *

"""
This program allows for interactive query from installed.db, which stores data about packages and extensions installed
on workstations.
"""

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
import ast
import contextlib
import getpass
import inspect
import json
import re
import sqlite3
mynetid = getpass.getuser()

###
# From hpclib
###
import linuxutils
from   urdecorators import trap
from sqlitedb import SQLiteDB
###
# imports and objects that are a part of this project
###
from packtuple import CompareTuple
import SQL_askdata 
verbose = False

###
# Credits
###
__author__ = 'Alina Enikeeva' 
__copyright__ = 'Copyright 2022'
__credits__ = None
__version__ = 0.1
__maintainer__ = 'Alina Enikeeva'
__email__ = ['alina.enikeeva@richmond.edu']
__status__ = 'in progress'
__license__ = 'MIT'

db_path = os.path.realpath("/home/milesdavis/packdata/installed.db")

mySQLstatements = SQL_askdata.mySQLstatements()
try:
    db = SQLiteDB(db_path)
except:
    db = None
    print(f"Unable to open {db_path}")
    sys.exit(EX_CONFIG)

con = sqlite3.connect(db_path)
cur = con.cursor()

@trap
def curator():
    """
    Finds out the name of the function that called it.
    Knowing the name of the functions will allow to find appropriate command in mySQLstatements dictionary based on the key.
    """
    #return inspect.stack()[1][3]
    previous_frame = inspect.currentframe().f_back.f_back
    function_name = inspect.getframeinfo(previous_frame)
    return function_name[2] 

@trap
def SQL_one(SQL) -> list:
    """
    Execute SQL statement for query to only one of the tables in the database.
    """
    try:
        return cur.execute(SQL).fetchall()
    except sqlite3.Error:
        pass

@trap
def SQL_two(SQL_installed, SQL_otherdata) -> list:
    """
    Execute SQL statement for queries to two tables in installed.db
    """
    try:
        installed = cur.execute(SQL_installed).fetchall() #returns list of tuples
        otherdata = cur.execute(SQL_otherdata).fetchall()
        return list(set(installed+otherdata))
    except sqlite3.Error:
        pass

@trap
def what_gpu(workstation:str) -> str:
    """
    Which gpu is installed on a workstation?
    """
    print("1", curator().strip("\'"))
    print("2", mySQLstatements[curator().strip("'")])
    print("3", SQL_one(mySQLstatements[curator()].format(workstation)))
    return [x[0] for x in SQL_one(mySQLstatements[curator()].format(workstation))]

@trap
def has_gpu() -> list:
    """
    Which workstations have GPUs?
    """
    #print("1", curator())
    #print("2", mySQLstatements[curator()])
    #print("3", SQL_one(mySQLstatements[curator()]))
    return [x[0] for x in SQL_one(mySQLstatements[curator()])]

@trap
def when_kernel_changed(workstation:str) -> str:
    """
    When did the kernel for a specific workstation last change?
    """
    result = SQL_one(mySQLstatements[curator()].format(workstation))
    return result[0][0] #[0][0] allows to return string as an ouput, not a tuple or a list

@trap
def workstations_updated_lastweek() -> list:
    """
    Which workstations were updated in the last week?
    """
    result = SQL_two(mySQLstatements[curator()][0],
                     mySQLstatements[curator()][1]) 
    return [x[0] for x in result]    

@trap
def which_linux_version(vrsn:str, workstation:str) -> bool:
    """
    Returns True if linux version of a specific workstation is less than vrsn - user input parameter. 
    """ 
    result = [x[0] for x in SQL_one(mySQLstatements[curator()].format(workstation))]
    #extract version number
    vrsn_db  = re.search("\d+\.\d+", result[0]).group()
    return vrsn_db<vrsn

@trap
def is_pkg_installed(pkg:str) -> list:
    """
    What workstations have a specific package installed?
    """
    return [x[0] for x in SQL_one(mySQLstatements[curator()].format(pkg))]

@trap
def pkg_not_installed(pkg:str) -> list:
    """
    What workstations do not have a specific package installed?
    """
    return [x[0] for x in SQL_one(mySQLstatements[curator()].format(pkg))]

@trap
def when_db_last_updated() -> str:
    """
    When was the database last updated?
    """
    result = max(SQL_two(mySQLstatements[curator()][0],
                         mySQLstatements[curator()][1]))
    return result[0]

@trap
def workstation_last_updated(workstation: str) -> str:
    """
    When specific workstation was last updated?
    """
    result =  max(SQL_two(mySQLstatements[curator()][0].format(workstation),
                          mySQLstatements[curator()][1].format(workstation)))
    return result[0]

@trap
def pkg_less_than_vsn(current_pkg:str, needed_pkg:str) -> bool:
    """
    Return True if the current version of the package is less than the needed one (the needed version is taken as an input from user.
    """
    obj = CompareTuple(current_pkg) 
    return obj<needed_pkg

@trap 
def workstations_outdated_pkgs(needed_pkg:str) -> dict:
    """
    What machines have outdated packages?
    The function returns a dictionary of the workstations that have an old version (which is less than needed_pkg) of the package installed.
    Each workstation in the dictionary has current version of the package installed as a value.
    """
    outdated_pkgs = {}
    # select all the workstations and packages where the name of the package starts with the name of the needed package
    # run a for loop for the list of packages and put the workstation name in the list if the package is less than the needed package
    needed_pkg_obj = CompareTuple(needed_pkg)
    packname = needed_pkg_obj.getPackname
    wrkst_have_pack = SQL_one(mySQLstatements[curator()].format(packname)) #extract a list with workstations that have a similar package installed
    for workstation, package_name in wrkst_have_pack:
        if package_name<needed_pkg_obj:
            outdated_pkgs[workstation]=package_name
    return outdated_pkgs
    
@trap
def askdata_main(myargs:argparse.Namespace) -> int:
    """
    print(has_gpu())
    print(which_linux_version("2.2", "anna")) #version number has to be a string to allow for comparison in the function
    print(when_kernel_changed("anna"))
    print(when_db_last_updated())
    print(workstation_last_updated("anna"))
    print(is_pkg_installed("xorg-x11-server-Xorg-1.20.4-22.el7_9.x86_64"))
    print(pkg_not_installed("xorg-x11-server-Xorg-1.20.4-22.el7_9.x86_64"))
    print(workstations_updated_lastweek())
    print(pkg_less_than_vsn("yelp-3.28.1-1.el7.x86_64", "yelp-4.28.1-2.el7.x86_64")) #first arg - current version, second arg - inputted
    print(workstations_outdated_pkgs("yelp-4.28.1-1.el7.x86_64"))
    """
    print(what_gpu("boyi"))
    return os.EX_OK


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog="askdata", 
        description="What askdata does, askdata does best.")
    parser.add_argument('--db', type=str, default=os.path.realpath("/home/milesdavis/packdata/installed.db"), 
        help="Input database name that contains information on packages and extensions installed on current workstations.")
    parser.add_argument('-i', '--input', type=str, default="",
        help="Input file name.")
    parser.add_argument('-o', '--output', type=str, default="",
        help="Output file name")
    parser.add_argument('-v', '--verbose', action='store_true',
        help="Be chatty about what is taking place")


    myargs = parser.parse_args()
    verbose = myargs.verbose
    #con = sqlite3.connect(myargs.db)
    #cur = con.cursor()
    #mySQLstatements = SQL_askdata.mySQLstatements()

    try:
        db = SQLiteDB(myargs.db)
    except:
        db = None
        print(f"Unable to open {myargs.db}")
        sys.exit(EX_CONFIG)

    try:
        outfile = sys.stdout if not myargs.output else open(myargs.output, 'w')
        with contextlib.redirect_stdout(outfile):
            sys.exit(globals()[f"{os.path.basename(__file__)[:-3]}_main"](myargs))

    except Exception as e:
        print(f"Escaped or re-raised exception: {e}")

