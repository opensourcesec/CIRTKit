#!/usr/bin/env python
# This file is part of Viper - https://github.com/cirtkit-framework/cirtkit
# See the file 'LICENSE' for copying permission.

import argparse

from lib.core.ui import console
from lib.core.investigation import __project__
from lib.core.database import Database

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--investigation', help='Specify a new or existing investigation name', action='store', required=False)
args = parser.parse_args()

if args.investigation:
    db = Database()
    __project__.open(args.investigation, db)

c = console.Console()
c.start()