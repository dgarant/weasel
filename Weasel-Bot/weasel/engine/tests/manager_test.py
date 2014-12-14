import unittest, os, iso8601, sqlite3, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from manager import BotManager
from dbmanager import DatabaseManager, DBError
from datetime import datetime, timedelta
from shared.config import EngineConfig

def is_iso_date_equal(date1, date2, minutes_error):
    """ Determines if two strings represent dates within minutes_error of each other

        Keyword arguments:
        date1 -- The first of the dates to compare
        date2 -- The second of the dates to compare
        minutes_error -- A number of minutes difference we will tolerate in our equality comparison
    """
    if type(date1) is str:
        date1 = iso8601.parse_date(date1) 
    if type(date2) is str:
        date2 = iso8601.parse_date(date2)

    tm_delta = abs(date1.replace(tzinfo=None) - date2.replace(tzinfo=None)).seconds
    if tm_delta > 60 * minutes_error:
        return False
    else:
        return True

class TestManagerUpdates(unittest.TestCase):
    """ A test case for the AccountManager updates """

    def setUp(self):
        """ Creates objects required by the test """
        config = EngineConfig(os.path.join(os.path.dirname(__file__), 'weasel.conf'))
        self.db_mgr = DatabaseManager(config)
        self.clear_bot_status()
        self.mgr = BotManager(config) 
        
    def tearDown(self):
        self.db_mgr.shutdown()

    def clear_bot_status(self):
        """ Clears the contents of the bot status, command log, and command map tables"""    
        try:
            self.db_mgr.exec_cmd('''delete from bot_status''', commit=True)
            self.db_mgr.exec_cmd('''delete from command_map''', commit=True)
            self.db_mgr.exec_cmd('''delete from command_log''', commit=True)
        except DBError, e:
            print("Error clearing database")
            raise e

    def test_create_if_new(self):
        test_ip = "0.0.0.0"
        self.mgr.create_if_new(test_ip) 
        try:
            rows = self.db_mgr.exec_query('select * from bot_status where ip = %s', test_ip)    
            self.assertEqual(len(rows), 1, "A new record for ip {0} was not created by create_if_new!".format(test_ip))
        except DBError, e:
            print("Error creating or querying test ip {0}".format(test_ip))
            raise e
        self.clear_bot_status()

    def test_handle_update(self):
        types = [('startup' , 'last_startup_time'),
                 ('shutdown' , 'last_shutdown_time'),
                 ('activity' , 'last_activity_time'),
                ]
        bot_ip = '0.0.0.0'
        for update_type in types:
            self.mgr.handle_update(bot_ip, update_type[0])
            try:
                rows = self.db_mgr.exec_query('select {0} from bot_status where ip = %s'.format(update_type[1]), bot_ip)
                self.assertEqual(len(rows), 1, "Got more than one record for bot {0} in the status table".format(bot_ip))
                self.assertIsNotNone(rows[0][0], "Failed to update {0}".format(update_type))
                self.assertTrue(is_iso_date_equal(rows[0][0], datetime.now().isoformat(), 1), 
                            "Expected current time {0} to be within 1 minute of update time {1}. Testing {2}."
                            .format(datetime.now(), rows[0][0], update_type))
            except DBError, e:
                print("Error while checking the bot status for update type {0}".format(update_type))
                raise e

    def create_past_date(self, days):
        """ Subtracts the specified number of days from 
            the current date and returned the new date in iso format
        """
        past_date = datetime.now() - timedelta(days=days)
        return past_date.isoformat()
        

    def load_test_bots(self):
        """ Load a set of bot records which can be used for a variety of tests 
            Return the ip addresses of the test bots
        """
        records = [
                    ('0.0.0.0', self.create_past_date(5), self.create_past_date(4), self.create_past_date(3), 32, 'A status message'),
                    ('0.0.0.1', self.create_past_date(0), self.create_past_date(0), self.create_past_date(0), 32, 'A status message'),
                    ('0.0.0.2', self.create_past_date(7), self.create_past_date(6), self.create_past_date(5), 32, 'A status message'),
                  ]
        for record in records:
            self.db_mgr.exec_cmd('''insert into bot_status (ip, last_startup_time, 
                                          last_activity_time, last_shutdown_time,
                                          port, message) VALUES (%s, %s, %s, %s, %s, %s)''',
                                          *record)
        return [r[0] for r in records]

    def test_clear_old_bots(self):
        self.clear_bot_status()
        self.load_test_bots()
        self.mgr.clear_old_bots(5) 
        records = self.db_mgr.exec_query('select * from bot_status')
        self.assertEqual(len(records), 2)
        self.clear_bot_status()

    def test_register_command(self):
        self.db_mgr.exec_cmd('delete from command_map')
        self.db_mgr.exec_cmd('delete from command_log')
        self.mgr.register_command('a command',  ['0.0.0.0', '0.0.0.1', '0.0.0.2'])
        rows = self.db_mgr.exec_query('select * from command_map')
        self.assertEqual(len(rows), 3, "The number of command map rows does not match the number of notified bots." + 
                                       "Command map content is {0}".format(rows))
        self.db_mgr.exec_cmd('delete from command_map')
        self.db_mgr.exec_cmd('delete from command_log')

    def test_active_bots(self):
        self.clear_bot_status()
        ip_addrs = self.load_test_bots()
        self.mgr.register_command('active bot command', ip_addrs)
        rows = self.mgr.get_active_bot_ips()
        self.assertEqual(len(rows), 0, "Expected no active bots, got {0}".format(len(rows)))
        self.db_mgr.exec_cmd('update bot_status set last_activity_time = %s', datetime.now().isoformat())
        rows = self.mgr.get_active_bot_ips()
        self.assertEqual(len(rows), 3, "Expected 3 active bots, got {0}".format(len(rows)))
        self.clear_bot_status()
        
    def test_send_to_active(self):
        self.clear_bot_status()
        self.mgr.send_to_active('ping')
        ip_addrs = self.load_test_bots()
        self.db_mgr.exec_cmd('update bot_status set last_activity_time = %s', datetime.now().isoformat())
        self.mgr.send_to_active('ping')
        self.clear_bot_status()

if __name__ == "__main__":
    unittest.main()
