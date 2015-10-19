
from lib.common.abstracts import Integration
from lib.common.out import *
from lib.core.database import Database

import yaml
import getpass
import argparse

from cbcmd import *


################
# Main Console #
################
class CarbonBlack(Integration):
    cmd = 'cb'
    description = 'CarbonBlack Live Response Console'
    authors = ['byt3smith']

    def __init__(self):
        super(CarbonBlack, self).__init__()
        self.active = True

    def stop(self):
        # Stop main loop.
        self.active = False

    def start(self, url, token, log):
        cli = CblrCli(url, token, log)
        # Main loop.
        while self.active:
            cli.prompt = cyan('CB ') + '> '
            cli.cmdloop()

    def load(self):
        # CLI argument declaration
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        log = 'integrations/carbonblack/http_cblr.log'

        # Get config from db
        db = Database()
        items = db.get_token_list()

        rows = []
        tokenOpts = {}
        for item in items:
            row = [item.id, item.app, item.user, item.fqdn]
            rows.append(row)
            tokenOpts[item.id] = {'token': item.apitoken, 'fqdn': item.fqdn}

        # Generate a table with the results.
        header = ['#', 'App', 'User', 'FQDN']
        print table(header=header, rows=rows)

        print_info("Select token by ID. Enter 0 to configure new profile:")
        choice = input("> ")

        # Form for new token profile configuration
        if int(choice) == 0:
            print("")
            print_info("Generating new Token profile")
            appname = "CarbonBlack"
            # If returned, create new token in db
            print_item("API Token:")
            token = raw_input("> ")
            print_item("Username (if applicable):")
            user = raw_input("> ")
            print_item("FQDN of remote server (format: ex.server.com:8000):")
            host = raw_input("> ")
            if len(user) == 0:
                user = ""

            db.add_token(token, user, appname, host)
            print_success("Token for {0} added successfully!".format(appname))
        elif int(choice) in tokenOpts:
            choice = int(choice)
            token = tokenOpts[choice]['token']
            host = tokenOpts[choice]['fqdn']
        else:
            print_error("Selection invalid. Try again")
            self.load()

        host = 'https://' + host

        # Start console!
        CarbonBlack().start(host, token, log)