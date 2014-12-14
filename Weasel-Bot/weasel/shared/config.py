#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Common classes for the Weasel Engine
#
# Author: Dan Garant
# Created: 8/6/12
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ConfigParser import ConfigParser

class EngineConfig:
    """ Object representation of configuration 
        information for the engine component
    """

    def __init__(self, config_path):
        """ Creates an engine configuration for 
            the config file located at config_path
        """
        config_parser = ConfigParser()
        config_parser.read(config_path)
        self.db_host = config_parser.get('database', 'host' )
        self.db_catalog = config_parser.get('database', 'catalog' )
        self.db_user = config_parser.get('database', 'user')
        self.db_pass = config_parser.get('database', 'password')
    
    def __str__(self):
        """ Returns a string representation of the configuration information"""
        return ("db host: {0}\ndb catalog{1}\nnotify address: {1}\n" + 
               "auth address: {2}\ncert file: {3}\nkey file: {4}\n"
               .format(self.db_host, self.db_catalog, self.notify_addr, 
                        self.auth_addr, self.cert_file, self.key_file))

class BotConfig:
    """ Object representation of bot configuration information
    """

    def __init__(self, config_path):
        """ Creates a bot configuration for the 
        config file at config_path 
        """
        config_parser = ConfigParser()
        config_parser.read(config_path)
        self.notify_addr = config_parser.get('master', 'notify_addr')
        self.server_port = int(config_parser.get('server', 'port'))
        self.validate_addr = config_parser.get('master', 'validate_addr')
        
        
