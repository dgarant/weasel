#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Account management for incoming connections to Weasel
#
# Author: Dan Garant
# Created: 08/08/12
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import hashlib, os, binascii 
from weasel.engine.dbmanager import DatabaseManager, DBError

class User:

    def __init__(self, ip, authenticated=False, active=False):
        self.ip = ip
        self.authenticated = False
        self.active=False
    
    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.ip)
        
class AccountManager:
    """ Weasel account management for web service"""

    def __init__(self, config):
        """ Initializes the account manager by 
            establishing a connection to the engine database
        """
        self.db_mgr = DatabaseManager(config)
        self.users = self._create_users()

    def _create_users(self):
        try:
            ips = self.db_mgr.exec_query('''select ip from account''')
        except DBError, e:
            print("Error occurred while building account list")
            raise e
        return [User(i[0], False, False) for i in ips]

    def get_account_ips(self):
        """ Get the IP addresses of all accounts in the system """
        users = self._create_users()
        return [u.ip for u in users]

    def drop_user(self, ip):
        """ Remove a user from the account table"""
        try:
            self.db_mgr.exec_cmd('''delete from account where ip=?''', ip)
        except DBError, e:
            print("Error occurred while deleting account for {0}".format(ip))
            raise e
        
    def get_user(self, ip):
        """ Obtains the user object identified by the given ip address"""
        matching = [u for u in self.users if u.ip ==  ip]
        if len(matching) > 0:
            return matching[0]
        else:
            return None

    def set_logged_in(self, ip):
        user = self.get_user(ip)
        user.authenticated = True
        user.active = True
        return user

    def test_authentication(self, ip, password):
        """ Tests the supplied authentication for validity.
            Returns True if the authentication is valid, False if invalid.

            Keyword arguments:
            ip -- The host to perform an authentication check on
            password -- The password to check
        """
        try:
            rows = self.db_mgr.exec_query('''select hash, salt from account
                                      where ip=?''', ip)
        except DBError, e:
            print("An error occurred obtaining auth info for ip {0}".format(ip))
            raise e
        if len(rows) == 0:
            return False
        expected_hash = rows[0][0]
        salt = rows[0][1]
        
        hashed_pw = hashlib.sha512(password + salt).hexdigest()

        if hashed_pw == expected_hash:
            return True
        else:
            return False

    def generate_salted_pass(self, password):
        """ Generates a salt and a hash for the given plaintext password.
            Returns a tuple (salt, hash)

            Keyword arguments:
            password -- The plaintext password to obtain a hash for
        """
        salt = binascii.b2a_hex(os.urandom(16))
        pwhash = hashlib.sha512(password + salt).hexdigest()
        return (salt, pwhash)

    def _create_new_account(self, ip, password):
        """ Creates a new account in the auth table """
        salt, pwhash = self.generate_salted_pass(password)
        try:
            self.db_mgr.exec_cmd('''insert into account (ip, hash, salt) values (?, ?, ?)''', ip, pwhash, salt)
        except DBError, e:
            print("An error occurred while creating an account for ip {0}: {1}".format(ip, e.args[0]))
            raise e
        
    def create_new_account(self, ip, password):
        """ Creates a new account in the authentication table 

            Keyword arguments:
            ip -- The ip address of the host to create an account for
            password -- The password to store for the new host entry 
        """
        self._create_new_account(ip, password)
        
    def change_account_password(self, ip, old_pass, new_pass):
        """ Changes the password in the authentication table for a given host

            Keyword arguments:
            ip -- The ip address of the host to change the password for
            old_pass -- The old password to use for authentication
            new_pass -- The new password
        """
        if self.test_authentication(ip, old_pass):
            salt, pwhash = self.generate_salted_pass(new_pass)
            try:
                self.db_mgr.exec_cmd('''update account set hash = ?, salt = ? where ip = ? ''', pwhash, salt, ip)
            except DBError, e:
                print("An error occurred while updating the password for ip {0}: {1}".format(ip, e.args[0]))
                raise e
        else:
            raise InvalidAuthException('Failed to authenticate host with IP {0}'.format(ip))
            
