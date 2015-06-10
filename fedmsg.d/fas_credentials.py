import getpass
import os


username = os.environ.get('BODHI_USER')
if not username:
    username = raw_input('FAS username: ')

if os.path.exists('/usr/bin/pass'):
    import sh  # You'll need to pip install this
    cmd = sh.Command('pass')
    password = cmd('sys/fas').strip()
else:
    password = getpass.getpass('FAS password: ')

config = {
    'fas_credentials': {
        'username': username,
        'password': password,
    }
}
