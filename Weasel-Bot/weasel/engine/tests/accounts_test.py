import unittest, os, sqlite3, sys
sys.path.append('..')
from manager import BotManager
from db_mgr import DatabaseManager, DBError

class TestConfiguration:
    def get_engine_database(self):
        return os.path.join(os.path.dirname(__file__), 'weasel.db')

class TestAccountManager(unittest.TestCase):
    """ A test case for the AccountManager updates """

    def setUp(self):
        """ Creates objects required by the test """
        config = TestConfiguration()
        self.db_mgr = DatabaseManager(config)
        self.mgr = AccountManager(config) 

    def test_create_account(

    
if __name__ == "__main__":
    unittest.main()
