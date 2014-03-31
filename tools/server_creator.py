'''
Demonstrates how you may create a server using the zabuza apis
'''
import getpass
import optparse
from os import environ
from zabuza.openstack import Api, User, PasswordCredential
from zabuza.services.compute import Server

def options_parser():
  parser = optparse.OptionsParser()
  parser.add_option('-u', '--user', help='username for authentication',
    dest='user', default=environ.get('ZABUZA_USERNAME') or None)
  parser.add_option('-p', '--password', help='password for authentication (Optional)',
    dest='password', default=environ.get('ZABUZA_PASSWORD') or None)
  parser.add_option('-a', '--adminurl', help='admin url for token exchange',
    dest='adminurl', default=environ.get('ZABUZA_TOKEN_URL') or None)
  parser.add_option('-t', '--tenant', help='tenant name to authenticate to',
    dest='tenant', default=environ.get('ZABUZA_TENANT_NAME') or None)

  opts, args = parser.parse_args()
  options_dict = {}
  #now, parse out options in 'logical' order
  if not opts.user:
    raise Exception('you must specify a user account for authentication')
  else:
    options_dict['user'] = opts.user

  if not opts.password:
    password = getpass.getpass('enter password for %s: '%opts.user)
    options_dict['password'] = password
  else:
    options_dict['password'] = opts.password


