import sqlite3
import os

DBError = sqlite3.Error

class DatabaseManager:
    """ Manages SQL operations on the Weasel database """
    
    def __init__(self, config):
        """ Initializes a bot manager with the given configuration.
            
            Keyword arguments:
            config -- The EngineConfig instance to use 
        """
        self.db_conn = sqlite3.connect(os.path.join(config.root_dir, config.db_catalog))

    def shutdown(self):
        """ Closes the database connection and decommits any active transactions"""
        self.db_conn.rollback()
        self.db_conn.close()

    def exec_query(self, command, *args):
        """ Executes an SQL query with the specified set of parameter values
            Returns a list of records matching the query
            
            Keyword arguments:
            command -- The command to execute
            *args -- Non-keyword arguments, specify positional parameter values to command
        """
        c = self.db_conn.cursor()
        try:
           c.execute(command, args) 
           results = c.fetchall()
        except DBError, e:
           raise e 
        finally:
            c.close()
        return results
    
    def exec_cmd(self, command, *args, **kwargs):
        """ Executes an SQL command with the specified set of parameter values
            
            Keyword arguments:
            command -- The command to execute
            *args -- Non-keyword arguments, specify positional parameter values to command
            commit -- Optional, defaults to True. Indicates that a 
                      commit should be performed after executing the statement
            lastrow -- Optional, defaults to False. Indicates if the execute statement 
                        should be treated as an insert statement and the id of the last 
                        inserted row should be returned.
        """
        return_item = None
        c = self.db_conn.cursor()
        try:
           c.execute(command, args) 
           if 'lastrow' in kwargs and kwargs['lastrow']:
               return_item = c.fetchone()[0]
           if "lastrowid" in kwargs and kwargs["lastrowid"]:
               return_item = c.lastrowid

           if 'commit' in kwargs:
               if kwargs['commit']:
                   self.db_conn.commit()
           else:
               self.db_conn.commit()
        except DBError, e:
           raise e 
        finally:
            c.close()

        return return_item
    
