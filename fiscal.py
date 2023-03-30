# -*- coding: utf-8 -*-
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
import cmd
import contextlib
import getpass
import parsec
import regex as re
import sqlite3
mynetid = getpass.getuser()

###
# From hpclib
###
import linuxutils
from   urdecorators import trap
from sqlitedb import SQLiteDB
sys.path.append('/home/milesdavis/fiscal/parkinglot')
from parse_fiscal import *
from askdata import *
from SQL_askdata import *
###
# imports and objects that are a part of this project
###
from textblob import TextBlob 
#from spellchecker import SpellChecker
verbose = False

###
# Credits
###
__author__ = "George Flanagin & Alina Enikeeva"
__copyright__ = 'Copyright 2023'
__credits__ = None
__version__ = 0.1
__maintainer__ = "Alina Enikeeva"
__email__ = ['hpc@richmond.edu']
__status__ = 'in progress'
__license__ = 'MIT'

# Something to print out when the program starts.
banner = (
    80*"$",
    "\t'I miss doing nothing most of all.' --- Lana del Rey",
    80*"$",
    " "
    )
db = None
workstations = []
keywords = []
class FiscalProgram(cmd.Cmd):
    """
    A basic command line program that does nothing except exit.
    """

    # Feed in the keystrokes exactly as entered.
    use_rawinput = True

    # These are class variables so that all the class's functions
    # can get to them.
    intro = "\n".join(banner)
    prompt = "\n[nothing]: "
    
    
    def __init__(self, myargs:argparse.Namespace):
        
        # There are many ways to call the base class's constructor.
        # I like this one because it is clearer (to me) what is
        # going on.
        cmd.Cmd.__init__(self)


    def preloop(self) -> None:
        """
        This function gets called just before the event loop 
        runs for the first time. Note that it does not return
        anything, and it does not need to be explicitly called.
        """
        global workstations, keywords
        #print("You are about to enter the event loop.")

        #open database        
        try:
            con = sqlite3.connect(myargs.db)
            cur = con.cursor()
        except:
            db = None
            print(f"Unable to open {myargs.db}")
            sys.exit(os.EX_CONFIG)

        #get the list of valid workstations names        
        SQL = """SELECT DISTINCT workstation FROM installed"""
        workstations = [x[0] for x in cur.execute(SQL).fetchall()]    
        #print(workstations) 
        #a list of valid prepositions
        prepositions = {
            "in": "in", #name of workstation should follow
            "on": "in",

            "than": "than", #Linux version OR package name should follow
            
            "with": "with", #package name should follow
            "where": "with",

            "in the past": "last", #number of days/period of time should follow
            "last": "last"
            
        }

        #a list of other valid keywords
        keywords = [
            "gpu",
            "gpus"
            "kernel",
            "updated",
            "linux",
            "version",
            "less than",
            "date",    
        ]
        
        return



    def precmd(self, text:str="") -> str:
        """
        This function is a 'hook' that allows you to do something before
        each command is interpreted.
        """
        global workstations, keywords
        #print(f"This is the precmd hook. In this case, we will lowercase the text.")

        # do the work on the first word of the command
        keyword_options = {
            "exit": "exit",
            "quit": "exit",
            "q": "exit",
            "bye": "exit",
    
            "show": "show",
            "what": "show",

            "list": "list"
        }
        
        cmd_parts = text.lower().split()
        try:
            cmd_parts[0] = keyword_options[cmd_parts[0]]
        except:
            return cmd.Cmd.precmd(self, " ".join(cmd_parts)) 

        ### do the work on the rest of the command

        # find out what you need to find
        what = ""

        ###find out where, i.e. what workstation is in the query

        #workstation_name = "irene"
        #WHITESPACE = parsec.regex(r'\s*', re.MULTILINE)
        #lexeme = lambda p: p << WHITESPACE
        #where = lexeme(parsec.string(workstation_name))
        #print(where)
        
        where = ""
        for idx, item in enumerate(cmd_parts):
            if (item in workstations):
                where = item
                break
            elif (item in keywords):
                what = item
            #else:
            #    print(f"Workstation name is invalid. Here is list of valid names {workstations}")
            
        #print("what", what)

        return cmd.Cmd.precmd(self, " ".join(cmd_parts))


    def emptyline(self) -> None:
        """
        Handle pressing the return key by itself. Print a line
        from King Lear.
        """
        print("This is emptyline(). Nothing will come of nothing. Speak again!")
        return cmd.Cmd.emptyline(self)
        

    def do_exit(self, text:str="") -> bool:
        """
        Just quit, after another shout from King Lear as 
        he banishes Cordelia.
        """
        print("This is do_exit(). Here I disclaim all my paternal care.")
        return True
 

    def default(self, text:str="") -> None:
        """
        This function handles all input situations that cannot
        be mapped into one of the do_* functions.
        """
        #example: "on boyi show gpu"
        parse_dct = user_input.parse(text)
         
        todo = parse_dct.get("command")
        todo = "".join([c for c in todo])
        
        what = parse_dct.get("subject")
        what = " ".join([s for s in what])
        
        where = parse_dct.get("workstations")
        where = " ".join([w for w in where]) 

        find_method = myKeysToSQL(where) # dict with existing methods as keys and necessary keywords as values
        for method, keywords in find_method.items():
            if set((keywords)) == set((todo, what, where)):
                call_method = dispatcher().get(method)
                print(call_method(where))
                 
                
        #print(f"Maybe try '{self.spellchecker(text)}' instead?")
        #print(f"'{text}' is nothing that I could understand. Try starting your command with 'list', 'show' or 'when'. Alternatively, type 'help' to see the list of valid prompts.")
        return cmd.Cmd.default(self, text)


    def postcmd(self, stop_flag:bool, userinput:str) -> bool:
        """
        stop_flag -- result of executing the user's command.
        userinput -- the user's command.
        """
        #print("This is the postcmd hook.") 
        #print(f"It received {stop_flag} from onecmd(), and")
        #print(f"the input was {userinput}")
        return cmd.Cmd.postcmd(self, stop_flag, userinput)


    def postloop(self) -> None:
        """
        This function is called after the loop concludes.
        """
        #print("This is the end, my friend. -- Jim Morrison")    
        sys.exit(os.EX_OK) 

   
    def spellchecker(self, text:str="") -> bool:
        prompt = TextBlob(text)
        return prompt.correct()
   
@trap
def fiscal_main(myargs:argparse.Namespace) -> int:
    """
    A function around the event loop.
    """

    # The only reason to put two lines in a function is to be
    # able to trap exceptions and print tombstones. The
    # following line creates a FiscalProgram instance,
    # and then calls the cmdloop() function to get things
    # going.
    try:
        myprog = FiscalProgram(myargs)
        myprog.cmdloop()

    except KeyboardInterrupt:
        # In any interactive program, you want to handle the user
        # typing control-C to break out.
        myprog.do_exit()
        print("Oh, you pressed control-C.")

    return os.EX_OK


if __name__ == '__main__':
    
    this_dir=os.path.dirname(os.path.realpath(__file__))
    parser = argparse.ArgumentParser(prog="skeletoncmd", 
        description="What fiscal does, fiscal does best.")

    parser.add_argument('-i', '--input', type=str, default="",
        help="Input file name.")
    parser.add_argument('-o', '--output', type=str, default="",
        help="Output file name")
    parser.add_argument('--db', type=str, default=os.path.realpath(f"{this_dir}/installed.db"),
        help="Input database name that contains information with packages installed on current workstations.")
    parser.add_argument('-v', '--verbose', action='store_true',
        help="Be chatty about what is taking place")


    myargs = parser.parse_args()
    verbose = myargs.verbose

    try:
        outfile = sys.stdout if not myargs.output else open(myargs.output, 'w')
        with contextlib.redirect_stdout(outfile):
            sys.exit(globals()[f"{os.path.basename(__file__)[:-3]}_main"](myargs))

    except Exception as e:
        print(f"Escaped or re-raised exception: {e}")

