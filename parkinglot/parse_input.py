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
import contextlib
import getpass
import re

try:
    import parsec
except ImportError as e:
    print("ijklparser requires parsec be installed.")
    sys.exit(os.EX_SOFTWARE)
mynetid = getpass.getuser()

###
# From hpclib
###
import linuxutils
from   urdecorators import trap
from parser_konstants import *
###
# imports and objects that are a part of this project
###
verbose = False

###
# Credits
###
__author__ = "Alina Enikeeva"
__copyright__ = 'Copyright 2022'
__credits__ = None
__version__ = 0.1
__maintainer__ = "Alina Enikeeva"
__email__ = ["alina.enikeeva@richmond.edu"]
__status__ = 'in progress'
__license__ = 'MIT'

WHITESPACE  = parsec.regex(r'\s*', re.MULTILINE)
lexeme = lambda p: p << WHITESPACE

workstations_lst = ['all', 'adam', 'anna', 'boyi', 'coltrane', 'dirac', 'elion', 'evan', 'franklin', 'hamilton', 'irene', 'justin', 'marie', 'newton', 'pople', 'quark', 'roald', 'sarah', 'spydur', 'thais']
prepositions_lst = ["in", "on", "of"]
keywords = [
            "gpu",
            "gpus"
            "kernel",
            "updated",
            "os",
            "linux",
            "version",
            "less than",
            "date",    
            "info"
        ]

next_word = parsec.regex(r'[a-z][-_a-z0-9]*')


class EndOfGenerator(StopIteration):
    def __init__(self, value):
        self.value = value

@lexeme
@parsec.generate
def preposition():
    p  = yield next_word
    if p in prepositions_lst:
        raise EndOfGenerator(p)

@parsec.generate
def workstation_name():
    yield preposition
    workstation_name = yield next_word
    if workstation_name in workstations_lst:
        raise EndOfGenerator(workstation_name)


WORKSTATION = workstation_name ^ preposition >> workstation_name

"""    
def subject():
    #yield command
    subject = yield next_word
    if subject in keywords:
        raise EndOfGenerator(subject)    
"""

#workstation = workstation_name | preposition >> workstation_name

"""
# user_input is unneeded.

next_word = parsec.regex(r'[a-z][-_a-z0-9]*')

The above statement defines next_word as a parser because that's 
the return type parsec.regex().

At that point, you just need:

yield next_word


@lexeme <<<<<<<<<<<<<<<< Explanations below.
@parser.generate <<<<<<<<<<<<
def preposition():
    p = yield next_word
    if p in prepositions_lst: 
        raise EndOfGenerator(p) <<<<<<<<<<<<<<<<<<<<


@parser.generate turns the Python function preposition() into a parser.
    It's magic!

@lexeme is a shortcut. Effectively, it is like doing the following
    later in the code:

            lexeme(preposition())

raise EndOfGenerator(p) I kind of forgot that return is best used
    only to leave the parsing operation. Sorry. I am having a difficult
    day. EndOfGenerator is in parser_konstants, and it is derived 
    from the Python built-in StopIteration. 

    Have you ever wondered how a for-loop knows that it gets to the
    end of your iterable list, tuple, dict? The generator that 
    goes through the data raises a StopIteration exception when there is
    no more to read. The for statement traps the exception and 
    ends it gracefully.

    Similarly, parsec traps StopIteration exceptions. The problem
    with StopIteration by itself is that it does not contain a
    value. It is just the event of stopping. It looks like this:

        class EndOfGenerator(StopIteration):
            def __init__(self, value):
                self.value = value


You can call the [hidden] parse function in preposition() like this:

        >>> preposition.parse('on')
        'on'
        >>> preposition.parse('off')
        >>> 

Note that it provides the preposition if it is in the list, otherwise
it returns nothing. 

The goal is to be able to write:

workstation = workstation_name | preposition >> workstation_name

... etc...

"""
"""
@parsec.generate
def user_input():
    input = yield parsec.regex(r'[a-z][-_a-z0-9]*')
    return input

parse_input = WHITESPACE >> user_input

@parsec.generate
def workstation_is() -> str:
    
    #Identifies the name of a workstation in input.
    
    preposition = yield parsec.regex(r'\s[a-z][a-z]\s') #valid prepositions are made up of two letters
    if preposition in prepositions_lst: #see if it is an actual preposition
        workstation_name = yield parsec.regex(r'{preposition}(?<=\s[a-z][a-z]).+'.format(preposition)) #matches the whole string after preposition
        workstation_name =  workstation_name.split(" ")[0] 
        if workstation_name in workstations_lst:
            return workstation_name
    return None

"""
@trap
def parse_input_main(myargs:argparse.Namespace) -> int:
    print(preposition.parse("find something on adam"))
    print(preposition.parse("on"))
    print(workstation_name.parse("in adam find whatever in adam"))
    return os.EX_OK


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog="parse_input", 
        description="What parse_input does, parse_input does best.")

    parser.add_argument('-i', '--input', type=str, default="",
        help="Input file name.")
    parser.add_argument('-o', '--output', type=str, default="",
        help="Output file name")
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

