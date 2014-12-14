#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Server process used to listen for and identify active bots
#
# Author: Dan Garant
# Created: 08/06/12
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import warnings, socket, ssl
from datetime import datetime, timedelta
from dbmanager import DatabaseManager, DBError

class BotManager:
    """ A class used to update information about online bots """
    
    def __init__(self, config):
        """ Initializes a bot manager with the given configuration.
            
            Keyword arguments:
            config -- The EngineConfig instance to use 
        """
        self.db_mgr = DatabaseManager(config)

    def create_if_new(self, ip):
        """ Determine if the host specified by ip exists in the bot status table,
            and creates an initial record if not
        """
        try:
            results = self.db_mgr.exec_query('select * from bot_status where ip = %s', ip)            
            if len(results) == 0:
               self.db_mgr.exec_cmd('''insert into bot_status (ip,  last_startup_time, last_shutdown_time, last_activity_time)
                            values (%s, %s, %s, %s)''', ip, None, None, None, commit=True)
        except DBError, e:
            print("Error occurred while querying bot status record exists for host {0}".format(ip))
            raise e


    def handle_update(self, ip, update, port=-1, message=""):
        """ Handles an update from a bot
    
            Keyword arguments:
            ip -- the ip address of the bot sending the update
            update -- A string representing the status of the bot
        """
        self.create_if_new(ip)

        # don't overwrite a valid port
        if port != -1:
            self.handle_port_update(ip, port)

        # always update the status message even if blank because
        # old messages become invalid
        self.handle_message_update(ip, message)

        lupdate = update.lower()
        if lupdate == 'startup':
            self.handle_startup(ip)
        elif lupdate == 'shutdown':
            self.handle_shutdown(ip)
        elif lupdate == 'ping':
            self.handle_ping(ip)
        elif lupdate == 'activity':
            self.handle_activity(ip)

    def handle_port_update(self, ip, port):
        """ Updates the port of the server sending from the specified ip""" 
        try:
            self.db_mgr.exec_cmd('update bot_status set port = %s where ip = %s', port, ip)
        except DBError, e:
            print("Error occurring updating the port of bot {0} to {1}".format(ip, port))
            raise e

    def handle_message_update(self, ip, message):
        """ Updates the status message of the server sending from the specified ip""" 
        try:
            self.db_mgr.exec_cmd('update bot_status set message = %s where ip = %s', message, ip)
        except DBError, e:
            print("Error occurring updating the status message of bot {0} to {1}".format(ip, message))
            raise e

    def handle_startup(self, ip):
        """ Handles a startup notification from a 
            bot at the specified ip address """
        try:
            self.db_mgr.exec_cmd('''update bot_status set last_startup_time = %s where ip = %s''', 
                                                    datetime.now().isoformat(), ip, commit=True)
        except DBError, e:
            print("Error occurred handling the startup status of the bot at ip {0}".format(ip)) 
            raise e

    def handle_shutdown(self, ip):
        """ Handles a shutdown notification from a 
            bot at the specified ip address """
        try:
            self.db_mgr.exec_cmd('''update bot_status set last_shutdown_time = %s where ip = %s''', 
                                        datetime.now().isoformat(), ip, commit=True)
        except DBError, e:
            print("Error occurred handling the startup status of the bot at ip {0}".format(ip)) 
            raise e

    def handle_ping(self, ip):
        """ Handles a ping notification (just an affirmation that the bot is alive)
            from a bot at the specified ip address """
        try:
            self.db_mgr.exec_cmd('''update bot_status set last_activity_time = %s where ip = %s''', 
                                    datetime.now().isoformat(), ip, commit=True)
        except DBError, e:
            print("Error occurred handling the startup status of the bot at ip {0}".format(ip)) 
            raise e

    def handle_activity(self, ip):
        """ Handles a notification of activity 
            from a bot at the specified ip address"""
        try:
            self.db_mgr.exec_cmd('''update bot_status set last_activity_time = %s where ip = %s''', 
                                                datetime.now().isoformat(), ip, commit=True)
        except DBError, e:
            print("Error occurred handling the startup status of the bot at ip {0}".format(ip)) 
            raise e

    def clear_old_bots(self, days):
        """ Clears old bots out of the status table

            Keyword arguments:
            days --- The number of days to maintain a bot in the 
                    status table if it is not sending updates
        """
        oldest_date = datetime.now() - timedelta(days=days)
        try:
            self.db_mgr.exec_cmd('delete from bot_status where last_activity_time < %s', oldest_date, commit=True)
        except DBError, e:
            print('Error occurred while clearing the bot history ' + 
                  'with oldest allowable date of {0}'.format(oldest_date))
            raise e
         

    def register_command(self, command_text, bot_ips):
        """ Registers a command in the database by storing a 
            log of the command body and the ip addresses of the target servers"""
        try:
            command_id = self.db_mgr.exec_cmd('insert into command_log (time, content) VALUES (%s, %s) returning command_id', 
                                      datetime.now().isoformat(), command_text, lastrow=True, commit=True)
            for ip in bot_ips:
                self.db_mgr.exec_cmd('insert into command_map (command_id, bot_ip) VALUES (%s, %s)',
                                     command_id, ip, commit=True)
        except DBError, e:
            print('Error occurred while registering ' + 
                  'command {0} to bots {1} in the database.'.format(command_text, bot_ips)) 
            raise e
        

    def get_active_bot_ips(self):
        """ Gets a collection of ip addresses and ports of bots 
            which are responding to commands as tuples (ip, port)
        """
        try:
            rows = self.db_mgr.exec_query('select max(time) from command_log having count(time) > 0') 
            if len(rows) == 0:
                warnings.warn('Did not find any commands in the command_log!', RuntimeWarning)
                return []
            last_cmd_time = rows[0][0]
            active_bots = self.db_mgr.exec_query('select ip, port from bot_status where ' + 
                                                '(last_activity_time > %s or last_startup_time > %s) '
                                                'and port > 0', last_cmd_time, last_cmd_time)
        except DBError, e:
            print('Error occurred while obtaining IP addresses of active bots')
            raise e
        return [(a[0], a[1]) for a in active_bots]

    def get_all_bots(self):
        try:
            bots = self.db_mgr.exec_query('select ip, port from bot_status')
        except DBError, e:
            print('Error occurred while obtaining bot status information')
            raise e
        return bots

    def validate_command(self, cmdhash):
        """ Determines if cmdhash matches the md5 hex digest of any 
            commands sent in the last 10 seconds """
        try:
            time_window = datetime.now() - timedelta(seconds=10)
            rows = self.db_mgr.exec_query('select * from command_log where md5(content) = %s and time > %s',
                                          cmdhash, time_window)
        except DBError, e:
            print("Error occurred while validating the command {0}".format(cmdhash))
            raise e
        return len(rows) >= 1

    def send_to_all(self, content):
        """ Connects to all bots and sends the specified content
            Arguments:
            content -- the string to transmit to the bots
        """
        bots = self.get_all_bots()
        return self.send(content, bots)

    def send_to_active(self, content):
        """ Connects to active bots and sends the content

            Arguments:
            content -- the string to transmit to the bots
        """
        bots = self.get_active_bot_ips()
        return self.send(content, bots)

    def send(self, content, bots):
        """ Sends a message to the specified bots """
        self.register_command(content, [b[0] for b in bots])
        success = []
        failed = []
        for connect_pair in bots:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s = ssl.wrap_socket(s)
                s.connect(connect_pair)
                s.send(content)
                s.shutdown(socket.SHUT_RDWR)
                s.close()
                success.append(connect_pair)
            except Exception, e:
                failed.append(connect_pair)
                continue
        return success, failed
                
