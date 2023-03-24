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
try:
    import parsec
except ImportError as e:
    sys.exit(os.EX_SOFTWARE)

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

workstations_lst = ['adam', 'anna', 'boyi', 'coltrane', 'dirac', 'elion', 'evan', 'franklin', 'hamilton', 'irene', 'justin', 'marie', 'newton', 'pople', 'quark', 'roald', 'sarah', 'spydur', 'thais']
prepositions_lst = ["in", "on", "of"]
keywords = [
            "gpu",
            "gpus",
            "kernel",
            "updated",
            "os",
            "linux",
            "version",
            "date"   
        ]

next_word = parsec.regex(r'[a-z][-_a-z0-9]*')
comma  = lexeme(parsec.string(COMMA))

class EndOfGenerator(StopIteration):
    def __init__(self, value):
        self.value = value

###
# The EndOfGenerator can raise .. anything .. as
# its value. What we would like to have is a collection
# of pairs, with the type of thing we found as the
# first element, and what we found as the second.
###
@lexeme
@parsec.generate
def subject():
    subject = yield next_word
    if subject in keywords:
        raise EndOfGenerator(("subject", subject)) 

###
# I'm beginning to rethink the optional preposition
# idea, and I now am considering that it should be
# required.
###
@lexeme
@parsec.generate
def preposition():
    word = yield next_word
    if word in prepositions_lst:
        raise EndOfGenerator(word)


###
# The name is fine.
###
@lexeme
@parsec.generate
def workstation_name():
    workstation_name = yield next_word
    if workstation_name in workstations_lst:
        raise EndOfGenerator(workstation_name)


###
# This is an example of how we might expand the 
# collection of data.
###
@parsec.generate
def workstation_list():
    ###
    # This is a basic comma separated list.
    ###
    names = yield parsec.sepBy(workstation_name, comma)
    raise EndOfGenerator(("workstations", [n for n in names if n]))


w0 = preposition > workstation_list 

text1 = "marie, franklin, coltrane"
text2 = "on boyi elion"
text3 = "on boyi, justin , hamilton"

for s in (text1, text2, text3):
    print(f"{s=} {w0.parse(s)=}")




