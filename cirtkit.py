#!/usr/bin/env python
# This file is part of Cirtkit - https://github.com/cirtkit-framework/cirtkit

import argparse
from sys import argv, executable
from os import path, symlink, getcwd

from lib.core.ui import console
from lib.core.investigation import __project__
from lib.core.database import Database

if argv[0][-3:] == '.py':
    # create symlink
    try:
        src = getcwd() + '/' + argv[0]
        dst = executable
        print dst
    except:
        pass

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--investigation', help='Specify a new or existing investigation', action='store', required=False)
args = parser.parse_args()

if args.investigation:
    db = Database()
    __project__.open(args.investigation, db)

c = console.Console()
c.start()
