from github3 import authorize
from getpass import getuser, getpass

user = "greglandrum"
password = ''

while not password:
    password = getpass('Password for {0}: '.format(user))

note = 'RDKit release note construction app'
note_url = 'http://rdkit.org'
scopes = ['user','repo']

auth = authorize(user, password, scopes, note, note_url)

with open(".git_tokens", 'w') as fd:
    fd.write(auth.token + '\n')
    fd.write(str(auth.id))
