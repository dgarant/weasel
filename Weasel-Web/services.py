import flask, os
from flask import Flask, request, render_template, flash, redirect
from flask_login import LoginManager, login_required, login_user
import sys

application = Flask(__name__)
WEASEL_ROOT = os.environ["WEASEL_ROOT"]
DEBUG=True

sys.path.append(WEASEL_ROOT)
from weasel.engine.manager import BotManager
from weasel.shared.config import EngineConfig
from weasel.engine.dbmanager import DatabaseManager
from weasel.engine.accounts import AccountManager, User

config = EngineConfig(os.path.join(WEASEL_ROOT, "weasel.conf"))

def read_private_key(config):
    """ Reads the private key required for secure sessions"""
    with open(os.path.join(WEASEL_ROOT, config.key_file), 'r') as key_file:
        lines = key_file.readlines()
        return lines[2]

application.secret_key = read_private_key(config)

act_mgr = AccountManager(config)
bot_mgr = BotManager(config)
db_mgr = DatabaseManager(config)

login_mgr = LoginManager()
login_mgr.setup_app(application)

login_mgr.login_view = "login"
login_mgr.login_message = u"You must login to continue"

@login_mgr.user_loader
def load_user(userid):
    return act_mgr.get_user(userid)

@application.route("/")
@login_required
def home_page_view():
    status_rows = db_mgr.exec_query('''select ip, last_startup_time, 
                                last_activity_time, last_shutdown_time,
                                port, message
                                from bot_status''')
    user_records = db_mgr.exec_query('''select ip, hash, salt from account''')
    command_records = db_mgr.exec_query('''select command_id, time, content 
                                    from command_log order by time desc limit 20''')
    return render_template('home_template.pt', user_records = user_records, 
                                               command_records = command_records,   
                                               status_records=status_rows)

@application.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    next = request.args.get('next')

    # post means the login form was submitted
    if request.method == 'POST':
        password = request.form['password']

        if act_mgr.test_authentication(request.remote_addr, password):
            user = act_mgr.set_logged_in(request.remote_addr)
            login_user(user)
            flash('Login successful')
            return redirect(next or '/')
        error = "Login failed"
    # re-render the login form on failure, or display for the first time
    return render_template('login.pt',next=next, error=error)

@application.route("/notify", methods=['GET'])
def notify():
    """ Handles status updates from bots
        Status should be one of startup, shutdown, ping, or activity
    """
    status = request.args['status']

    port = -1
    if 'port' in request.args:
       port = request.args['port'] 

    message = ""
    if 'message' in request.args:
        message = request.args['message']

    ip = request.remote_addr
    bot_mgr.handle_update(ip, status, port, message)
    return "Updated status of bot {0} to {1}, {2}, {3}".format(ip, status, port, message)

@application.route("/validate", methods=['GET'])
def validate():
    """ Determines if the specified MD5 hash 
        matches the content of commands in the past 10 seconds """
    hash = request.args['command']
    return str(bot_mgr.validate_command(hash))

if __name__ == "__main__":
    application.run()
