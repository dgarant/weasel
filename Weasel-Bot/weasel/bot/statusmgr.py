import urllib


class StatusManager:
    """ Handles status updates to the server """

    def __init__(self, port, config):
        """ Initializes a status manager with the given configuration"""
        self.config = config
        self.port = port

    def _get_request(self, baseurl, params):
        """ Initiates a get request to the server with the given parameters.
            Returns the response
            Arguments:
            baseurl -- The url (without trailing question mark) to request
            params -- The parameters to pass in the get request
        """
        webparams = urllib.urlencode(params)
        response = urllib.urlopen("{0}?{1}".format(baseurl, webparams))
        return response.read()

    def validate_cmd_hash(self, cmd_hash):
        """ Confirms with the bot manager that it requested a specific action 
            Return true if the action was requested, false otherwise.

            Arguments:
            cmd_hash -- The MD5 hash of the received command to verify
        """
        response = self._get_request(self.config.validate_addr,
                                    {'command' : cmd_hash})
        if response.lower() == 'true':
            return True
        else:
            return False

    def notify_startup(self, message=''):
        """ Notifies the bot manager that we have started up with the specified message"""
        response = self._get_request(self.config.notify_addr, 
                            {'status' : 'startup', 'port' : self.port, 'message' : message})
        return response

    def notify_shutdown(self, message=''):
        """ Notifies the bot manager that the server shutdown """
        response = self._get_request(self.config.notify_addr,
                                {'status' : 'shutdown', 'port' : self.port, 'message' : message})
        return response

    def notify_ping(self, message='Responding to a ping'):
        """ Responds to a ping received from the bot manager """
        response = self._get_request(self.config.notify_addr,
                                {'status' : 'ping', 'port' : self.port, 'message' : message})
        return response

    def notify_activity(self, message='Performed an activity'):
        """ Notifies the bot manager that we are performing an activity"""
        response = self._get_request(self.config.notify_addr,
                                {'status' : 'activity', 'port' : self.port, 'message' : message})
        return response

   
