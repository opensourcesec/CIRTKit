# This file is part of Viper - https://github.com/viper-framework/viper
# See the file 'LICENSE' for copying permission.

import os
import shutil

class Investigation(object):
    def __init__(self):
        self.name = None
        self.path = None

    def open(self, name, db):
        path = os.path.join(os.getcwd(), 'investigations', name)
        if not os.path.exists(path):
            os.makedirs(path)  # Create the dir for the current investigation
            os.makedirs(path + '/notes')  # Create dir for storing notes in the current investigation

        self.name = name
        self.path = path

        db.add_investigation()

    def get_path(self):
        if self.path and os.path.exists(self.path):
            return self.path
        else:
            return os.getcwd()

    def delete(self, investid, db):
        path = db.get_investigation_path(investid)
        shutil.rmtree(path, ignore_errors=True)
        db.remove_investigation(investid)

__project__ = Investigation()
