'''
Demonstrates how you may create a server using the zabuza apis
'''
import getpass
import optparse
from os import environ
from zabuza.openstack import Api, User, PasswordCredential
from zabuza.services.compute import Server

########################################
#     Utility Functions and Globals
########################################
user = None #TODO store somewhere for future use

def options_parser():
  parser = optparse.OptionParser()
  parser.add_option('-u', '--user', help='username for authentication (Required)',
    dest='user', default=environ.get('ZABUZA_USERNAME') or None)
  parser.add_option('-p', '--password', help='password for authentication (Optional)',
    dest='password', default=environ.get('ZABUZA_PASSWORD') or None)
  parser.add_option('-a', '--adminurl', help='admin url for token exchange (Required)',
    dest='adminurl', default=environ.get('ZABUZA_TOKEN_URL') or None)
  parser.add_option('-t', '--tenant', help='tenant name to authenticate to (Required)',
    dest='tenant', default=environ.get('ZABUZA_TENANT_NAME') or None)
  parser.add_option('-o', '--operation', 
    help='[create | read | update | delete] operations (Optional)',
    dest='operation', default='read')
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

  if not opts.admin_url:
    raise Exception('you must specify an admin url endpoint for authentication')
  else:
    options_dict['adminurl'] = opts.adminurl

  if not opts.tenant:
    raise Exception('you must specify a tenant')
  else:
    options_dict['tenant'] = opts.tenant

  options_dict['operation'] = opts.operation

  return options_dict

def great_expectations(expects, reality):
  '''
  ensures that expectations match reality :-)

  that is answers the question, are all expected params defined?
  '''
  for expectation in expects:
    if expectation not in reality:
      return (False, expectation)

def authenticator(options):
  '''
  authenticates with api
  '''
  global user
  user = User(options['adminurl'],
    username=options.get('user'),
    password=options.get('password'),
    tenant_name=options.get('tenant'))
  user.authenticate()


##################################
          Action Handlers
##################################
def create(options):
  expects = ['image', 'flavor', 'name']
  reality, issue = great_expectations(expects, options)
  if not reality:
    raise Exception('you must specify %s'%issue)
  

#################################
          Action Switch
##################################
def executor(options):
  '''
  determines what operation you want to execute and then delegates it to
  method implementing said interface
  '''
  if options['operation'] == 'create':
    #TODO creaty stuff
    pass
  elif options['operation'] == 'read':
    #TODO ready stuff
    pass
  elif options['operation'] == 'update':
    raise NotImplementedError #unsupported by api
  elif options['operation'] = 'delete':
    raise NotImplementedError #unsupported by api

if __name__ == '__main__':
  executor(options_parser())
