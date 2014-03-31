'''
full fledged command like client for managing server
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
  parser.add_option('-i', '--image', help='image id', dest='image',
    default=None)
  parser.add_option('-f', '--flavor', help='flavor id', dest='flavor',
    default=None)
  parser.add_option('-n', '--name', help='compute server name', dest='name',
    default=None)

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

  if not opts.adminurl:
    raise Exception('you must specify an admin url endpoint for authentication')
  else:
    options_dict['adminurl'] = opts.adminurl

  if not opts.tenant:
    raise Exception('you must specify a tenant')
  else:
    options_dict['tenant'] = opts.tenant

  supported_operations = ['create', 'read', 'update', 'delete']
  if opts.operation not in supported_operations:
    raise Exception('we only support following operations %s'%supported_operations)
  else:
    options_dict['operation'] = opts.operation
  
  if opts.image:
    options_dict['image'] = opts.image
  if opts.flavor:
    options_dict['flavor'] = opts.flavor
  if opts.name:
    options_dict['name'] = opts.name

  return options_dict

def great_expectations(expects, reality):
  '''
  ensures that expectations match reality :-)

  that is answers the question, are all expected params defined?
  '''
  for expectation in expects:
    if expectation not in reality:
      return (False, expectation)
  return (True, '')

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
#          Action Handlers
##################################
def create(options):
  global user
  expects = ['image', 'flavor', 'name']
  reality, issue = great_expectations(expects, options)
  if not reality:
    raise Exception('you must specify a(n) %s'%issue)
  api = Api(options['adminurl'], user=user)
  server = Server.create_server_for_deployment(options['image'],
    options['flavor'], options['name'])
  kwargs = {}
  kwargs['user_data_file'] = options.get('userdatafile', None)
  if 'computetype' in options:
    kwargs['compute_type'] = options.get('computetype')
  kwargs['key_name'] = options.get('keyname')

  result = api.create_server(server, **kwargs)

  print result

#################################
#          Action Switch
##################################
def executor(options):
  '''
  determines what operation you want to execute and then delegates it to
  method implementing said interface
  '''
  authenticator(options)
  if options['operation'] == 'create':
    create(options)
  elif options['operation'] == 'read':
    #TODO ready stuff
    pass
  elif options['operation'] == 'update':
    raise NotImplementedError #unsupported by api
  elif options['operation'] == 'delete':
    raise NotImplementedError #unsupported by api

if __name__ == '__main__':
  executor(options_parser())
