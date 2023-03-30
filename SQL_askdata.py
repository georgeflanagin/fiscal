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
mynetid = getpass.getuser()

###
# From hpclib
###
import linuxutils
from   urdecorators import trap

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

@trap
def mySQLstatements() -> dict:
    
    #keys = ("has_gpu", "when_kernel_changed", "which_linux_version", "is_pkg_installed", "pkg_not_installed", "when_db_last_updated", "workstation_last_updated", "workstations_updated_lastweek", "workstations_outdated_pkgs")

    #values = ("""SELECT workstation FROM otherdata WHERE inquiry = 'gpu_driver' AND result != 'None'""", 
    #        """SELECT first_seen FROM otherdata WHERE inquiry = 'linux_after_reboot' AND workstation = '{}' ORDER BY first_seen DESC LIMIT 1""",
    #         """SELECT result FROM otherdata WHERE inquiry = 'redhat_os' AND workstation = '{}' ORDER BY first_seen DESC LIMIT 1""",
    #        """SELECT workstation FROM installed WHERE package_name = '{}'""",
    #         """SELECT DISTINCT workstation FROM installed WHERE workstation NOT IN (SELECT workstation FROM installed WHERE package_name = '{}')""",
    #        ("""SELECT MAX(first_seen) FROM installed""","""SELECT MAX(first_seen) FROM otherdata"""),
    #        ("""SELECT first_seen FROM installed WHERE workstation = '{}' ORDER BY first_seen DESC LIMIT 1""", """SELECT first_seen FROM otherdata WHERE workstation = '{}'  ORDER BY first_seen DESC LIMIT 1"""),
    #        ("""SELECT DISTINCT workstation FROM installed WHERE first_seen>=date() - 7""", """SELECT DISTINCT workstation FROM otherdata WHERE first_seen>=date() - 7"""),
    #        """SELECT workstation, package_name FROM installed WHERE package_name GLOB '{}*'""")
    

    keys = ('what_gpu', "has_gpu")
    values = ("""select result, max(first_seen) from v_gpu where workstation = '{}'""", "ddd")

    return dict(zip(keys, values))        


@trap
def SQL_askdata_main(myargs:argparse.Namespace) -> int:
    print(mySQLstatements())
    return os.EX_OK


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog="SQL_askdata", 
        description="What SQL_askdata does, SQL_askdata does best.")

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

