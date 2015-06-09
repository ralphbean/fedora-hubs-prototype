import commands
import getpass
import os

username = os.environ.get('BODHI_USER')
if not username:
    username = raw_input('FAS username: ')

if os.path.exists('/usr/bin/pass'):
    password = commands.getoutput('pass sys/fas')
else:
    password = getpass.getpass('FAS password: ')

config = {
    'fas_credentials': {
        'username': username,
        'password': password,
    }
}
