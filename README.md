weasel
======

A platform for remote code execution to facilitate network security research

Setup Instructions
-----------------

Define an environment variable `WEASEL_ROOT` that points to the location of your Weasel-Bot directory.

Install dependencies:
```bash
pip install -r requirements.txt
```

Create sqlite3 database:
```bash
cd Weasel-Bot
sqlite3 weasel.s3db < ../schema.sql
```

Test out the botmaster configuration:
```bash
$python executor.py
weasel> help

Documented commands (type help <topic>):
========================================
EOF  active  createuser  dropuser  exec  help  ping  put  showusers

weasel> ping
Success [] Failure []
weasel> createuser 127.0.0.1 mysecretpassword
Created user 127.0.0.1
```


Start the web-based services:
```bash
cd Weasel-Web
$python services.py
 * Running on http://127.0.0.1:5000/
```

Modify `bot.conf` to refer to the server addresses. In this case:
```
[master]
notify_addr=http://127.0.0.1:5000/notify
validate_addr=http://127.0.0.1:5000/validate
```

Start up a bot:
```bash
$python bot_server.py
('127.0.0.1', 5507)
```

Make sure the bot is responding and send it a script:
```bash
$python executor.py
weasel> ping
Success [(u'127.0.0.1', 5507)] Failure []
weasel> put /Users/dgarant/repos/weasel/Weasel-Bot/weasel/bot/scripts/say-hello-simple.py
Success [(u'127.0.0.1', 5507)] Failure []
weasel> exec say-hello-simple.py
```

The bot should respond to the command and print out "hello".


