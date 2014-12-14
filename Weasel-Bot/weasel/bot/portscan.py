import socket, ssl


class PortScanner:
    """ Finds open paths between this host and a specified host """

    def __init__(self, target):
        """ Initializes the port scanner with the specified target host""" 
        self.target_host = target

    def run_scan(self):
        """ Runs a scan against a collection of ports.
            Returns ports which can be used to connect to the target 
            Returns a tuple (open, closed)
        """
        open_ports = []
        closed_ports = []
        for port in range(1, 3000):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock = ssl.wrap_socket(s)
                sock.connect((target, port))
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
                ports.append(port)
            except Exception, e:
                closed_ports.append(port)
        return open_ports, closed_ports
            
