import requests
import logging
import base64
from random import choice
from traceback import format_exc
from datetime import datetime
from dateutil.parser import parse as dateparser
from services.compute import Server
try:
  from json import loads, dumps
except ImportError:
  from simplejson  import loads, dumps

class Endpoint(object):
  '''
  A representation of a service endpoint which the authenticated user
  can talk to.
  '''
  #TODO: refactor into base entities.
  def __init__(self, *args, **kwargs):
    '''
    Expected keyword arguments:
    admin_url: a url representing administration url of this service
    region: what region is this service in
    internal_url: internal url used to access this service
    id: an id representing this endpoint's identifier in keystone
    public_url: public url used to access this service
    type: a valid nova service type string e.g volume, image

    Note: these also supports openstack camel case args passing e.g
    instead of specifying admin_url you could pass adminURL etc
    '''
    self._admin_url = kwargs.get('admin_url') or kwargs.get('adminURL')
    self._region = kwargs.get('region')
    self._internal_url = kwargs.get('internal_url') or kwargs.get('internalURL')
    self._id = kwargs['id']
    self._public_url = kwargs.get('public_url') or kwargs.get('publicURL')
    self._type = kwargs['type']
    self._name = kwargs['name']

  @property
  def id(self):
    return self._id

  @property
  def region(self):
    return self._expires

  @property
  def internal_url(self):
    return self._internal_url

  @property
  def public_url(self):
    return self._public_url

  @property
  def type(self):
    return self._type

  @property
  def name(self):
    return self._name

  def fetch_url(self, path):
    '''
    Construct a proper url given a path
    Args:
      path:
        a list of all string tokens in a path e.g [foo, bar, vim] which
        corresponds to <base_url>/foo/bar/vim
    '''
    if type(path) != list:
      path = [path]
    return '/'.join([self._public_url]+path)

  def __eq__(self, other):
    assert isinstance(other, Endpoint)
    if self.admin_url != other.admin_url:
      return False

    if self.region != other.region:
      return False

    if self.internal_url != other.internal_url:
      return False

    if self.id != other.id:
      return False

    if self.public_url != other.public_url:
      return False
    
    return True


class ServiceCatalog(object):
  '''
  A representation of a service catalog.
  Allows you to retrieve endpoints of a specific service
  '''
  def __init__(self, *args, **kwargs):
    '''
    Expected keyword arguments:
    service_catalog: a service catalog list object returned by keystone 
    '''
    #break if there is no endpoints key
    self._catalog = dict()
    sc = kwargs.get('service_catalog') or kwargs.get('serviceCatalog')
    assert sc is not None
    for service in sc:
      atype, aname = service['type'], service['name']
      if atype not in self._catalog:
        self._catalog[atype] = []
      for endpoint in service['endpoints']:
        self._catalog[atype].append(Endpoint(name=aname, type=atype, **endpoint))

  def get_endpoint_for(self, service_type, region=None):
    '''
    Supported service_types include:
      s3, volumev2, network, compute, computev3
    '''
    if service_type not in self._catalog:
      logging.debug('here is service catalog: %s'%self._catalog)
      logging.debug('here is service_type %s'%service_type)
      raise ValueError('Unrecognized service type endpoint specified')
    selector = lambda endpoints: choice(endpoints)
    if not region:
      return selector(self._catalog[service_type])
    else:
      return filter(lambda x: x.region == region, self._catalog[service_type])

class Token(object):
  '''
  A representation of a token credential obtained from keystone
  '''
  def __init__(self, *args, **kwargs):
    '''
    Expected keyword arguments:
    id: token id string
    expires: ISO-8601 string representation of expiry time
    issued_at: ISO-8601 string representation of time of issue
    tenant: tenant name this token is associated with
    '''
    #Fail if any expected parameter is not available.
    self._id = kwargs['id']
    self._expires = dateparser(kwargs['expires'])
    self._issued_at = dateparser(kwargs['issued_at'])
    self._tenant = kwargs['tenant']

  @property
  def id(self):
    return self._id
  
  @property
  def expires(self):
    return self._expires

  @property
  def issued_at(self):
    return self._issued_at

  @property
  def tenant(self):
    return self._tenant

  def __str__(self):
    return self._id

  def __repr__(self):
    return self._id

class PasswordCredential(object):
  '''
  A representation of the password credentials object required
  by keystone before exchanging with a token
  '''
  def __init__(self, username=None, password=None):
    self._username = username
    self._password = password

  @property
  def username(self):
    return self._username

  @property
  def password(self):
    return self._password

  @property
  def json(self):
    return dumps({'username': self.username,
                  'password': self.password})
  
  @property
  def python_dict(self):
    return {'username': self.username,
            'password': self.password}

  def is_valid(self):
    return self.username != None and self.password != None

  def __str__(self):
    return 'username: %s password: %s'%(self._username, self._password)

class User(object):
  '''
  An abstract representation of an openstack user.
  Handles authentication of current user.
  '''
  def __init__(self, auth_url, username=None, password=None, token=None,
    tenant_name=None):
    self._credentials = PasswordCredential(username, password)
    if type(token) == Token:
      self._token = token
    elif token != None:
      raise Exception('supplied token must be a Token object')
    else:
      self._token = None
    
    self.tenant_name = tenant_name
    self.auth_url = auth_url
    self._id = None
    self._username = None
    self._name = None
    self._roles = []
    self._catalog = None


  def _get_credentials(self):
    return self._credentials

  def _set_credentials(self, cred):
    assert isinstance(PasswordCredentials, cred)
    self._credentials = cred
  
  def _del_credentials(self):
    del self._credentials

  credentials = property(_get_credentials, 
    _set_credentials, 
    _del_credentials,
    "credentials property")

  @property
  def id(self):
    return self._id

  @property
  def username(self):
    return self._username

  @property
  def name(self):
    return self._name

  @property
  def roles(self):
    return self._roles

  @property
  def token(self):
    return self._token

  def is_authenticated(self):
    '''
    Verified that we have and can authenticate against the openstack API.
    Note that all operations done against the API will use your token supplied
    not your username/password pair. This routine also validates that our token
    is still valid.

    Note, it simple checks that there is a token and its expiry is set for the
    future. So, if a token has been revoked it is possible this will still
    return success.
    '''
    if self.token:
      return self.token.expires.replace(tzinfo=None) > datetime.now()
    else:
      return False


  def authenticate(self):
    '''
    Re-authenticate with the API by getting a brand spanking new token
    Raises appropriate errors if authentication failed otherwise proceeds as
    normal.
    '''
    if not self._can_authenticate():
      raise AttributeError('Either token or credentials must be available')
    post_data = {'auth': {}}
    if self.token:
      post_data['auth']['token'] = token
    else:
      post_data['auth']['passwordCredentials'] = self.credentials.python_dict

    post_data['auth']['tenantName'] = self.tenant_name
    logging.debug('authenticate data: %s'%dumps(post_data))
    response = requests.post(self.auth_url, 
      data=dumps(post_data),
      headers={'content-type':'application/json'})
    if response.status_code == requests.codes.ok:
      data_dict = response.json()
      self._update_token(data_dict)
      self._update_user(data_dict)
    else:
      response.raise_for_status()
    
  def endpoint_manager(self, service_name, **kwargs):
    '''
    convenience function for service catalog's get_endpoint_for func
    '''
    return self._catalog.get_endpoint_for(service_name, **kwargs)

  def _update_token(self, data_dict):
    token_info = data_dict['access']['token']
    self._token = Token(**token_info)

  def _update_user(self, data_dict):
    '''
    Given the response from the token creation POST, set our user information
    from the info returned by the Keystone service
    '''
    user_info = data_dict['access']['user']
    #some of these are optional and so dont break if not present
    self._id = user_info.get('id', None)
    self._name = user_info.get('name', None)
    self._username = user_info.get('username', None)
    self._roles = user_info.get('roles', None)
    self._catalog = ServiceCatalog(**data_dict['access'])

  def _can_authenticate(self):
    '''
    Verify that all the parameters necessary for authentication has been made
    present:
      username, password / token, tenant_name
    '''
    if not self.token:
      logging.debug('no token available, checking if credentials valid')
      if not self.credentials.is_valid():
        logging.debug('credentials invalid')
        return False
    else:
      logging.debug('a token is available, checking if unexpired')
      return self.is_authenticated()

    if not self.tenant_name:
      return False
    
    if self.auth_url == '' or self.auth_url == None:
      return False

    return True

  def __str__(self):
    return 'token: %s, tenant:%s'%(self.token, self.tenant_name)
    
class Api(object):
  '''
  A simple proxy object that delegates a lot of openstack service
  functions to actual service implementation modules.
  '''

  def __init__(self, auth_url, username=None, password=None, token=None,
    tenant_name=None, user=None):
    '''
    The base API object representing virtually all openstack service calls.

    Args:
      auth_url:
        the admin url where tokens can be generated and authenticated. [Required]
      username:
        user you want this application to run as in keystone [Optional]
      password:
        associated password of user [Optional]
      token:
        a previously generated Token object [Optional]
      tenant_name:
        what tenant will I be running under
      user:
        a user object previously generated [Optional]

      Note, either the username and password or token must be specified unless
      you have provided a user object
    '''
    if user:
      assert isinstance(user, User)
      self.user = user
    else:
      self.user = User(auth_url, username=username, password=password,
        token=token, tenant_name=tenant_name)
    self.errors = []

  def verify_credentials(self):
    '''
    Have we specified valid credentials which we can perform openstack
    operations with

    returns a boolean indicate if verification was successful or not
    '''
    if self.user.is_authenticated():
      return True
    else:
      try:
        self.user.authenticate()
      except Exception as ex:
        exc = format_exc()
        self.errors.append(exc)
        self.errors.append(str(ex))
      else:
        return True
    return False
  
  def create_server(self, server, user_data_file=None, user=None,
                    compute_type='compute', key_name=None):
    '''
    Create a new server. The main required parameter is a server.

    Args:
      server:
        a server object. recommended to create with the
        create_server_for_deployment factory method in Server object.
      user_data_file:
        file path to a user data file
      user:
        a user object that has been authenticated
      compute_type:
        type of compute, e.g compute or computev3
      key_name:
        name of ssh_key to be included in server for initial login
    '''
    user = user or self.user
    self._assert_preconditions(user=user)
    endpoint = self.user.endpoint_manager(compute_type)
    url = endpoint.fetch_url(['servers'])

    #now, construct parameters
    parameters = {'server': {}}
    parameters['server']['flavorRef'] = server.flavor
    parameters['server']['imageRef'] = server.image
    parameters['server']['name'] = server.name
    if server.availability_zone:
      parameters['server']['availability_zone'] = server.availability_zone
    if server.metadata:
      parameters['server']['metadata'] = server.metadata
    if server.security_group_name:
      parameters['server']['security_group'] = server.security_group_name
    if user_data_file:
      parameters['server']['user_data'] = base64.b64encode(open(user_data_file).read())
    if key_name:
      parameters['server']['key_name'] = key_name

    logging.debug('now creating server %s at url %s'%(parameters, url))
    json_data = self._post_url(url, parameters)
    logging.debug('returned data was %s'%json_data)
    server.update_properties(**json_data['server'])
  
  def get_server_detail(self, server=None, server_id=None, user=None,
                        compute_type='compute'):
    '''
    Get details of a specific server. 

    Args:
      server:
        a server object. [Optional]
      server_id:
        id of server we want info on [Optional]
      user:
        a user object that has been authenticated
      compute_type:
        type of compute, e.g compute or computev3

    Note that either the server or server_id must be specified.
    '''
    user = user or self.user
    self._assert_preconditions(user=user)
    if not server:
      if not server_id or server_id == '':
        raise Exception('either a server or server_id must be specified')
    
    server_id = server_id or server.id
    endpoint = user.endpoint_manager(compute_type)
    url = endpoint.fetch_url(['servers', server_id])

    logging.debug('now fetching details of a specific server with url %s'%(url))
    json_data = self._get_url(url)
    return Server.create_server(**json_data['server']) 

  def get_servers_detail(self, flavor=None, name=None, marker=None,
                        limit=None, status=None, changes_since=None, host=None, 
                        user=None, compute_type='compute'):
    '''
    Get details of all servers.
    
    The optional args are for filtering purposes.
    
    Args:
      flavor:
        string. what flavors of servers to return data for [Optional]
      name:
        servers that match what name string? [Optional]
      marker:
        UUID for the server you want to set a marker [Optional]
      limit:
        integer, size of the information list returned [Optional]
      status:
        what status should the servers be? example 'ACTIVE' [Optional]
      host:
        host on which these servers are deployed on [Optional]
      changes_since:
        a date or timestamp string when the server last changed status [Optional]
      user:
        an authenticated user this request should be executed as
      compute_type:
        type of compute, e.g compute or computev3
    '''
    user = user or self.user
    self._assert_preconditions(user=user)
    endpoint = user.endpoint_manager(compute_type)
    url = endpoint.fetch_url(['servers', 'detail'])

    #construct filtering parameters
    parameters = {}
    if flavor:
      parameters['flavor'] = flavor
    if name:
      parameters['name'] = name
    if limit: #TODO: support for next batch of servers?
      try:
        assert type(limit) is int
      except AssertionError:
        raise Exception('limit must be an integer')
      else:
        parameters['limit'] = limit
    if host:
      parameters['host'] = host
    if status:
      parameters['status'] = status
    if changes_since:
      parameters['changes_since'] = str(dateparser.parse(changes_since))

    logging.debug('now fetching details with url %s and options %s'%(url, parameters))
    json_data = self._get_url(url, parameters=parameters)
    servers = []
    for server_json in json_data['servers']:
      servers.append(Server.create_server(**server_json))
    return servers

  def delete_server(self, server=None, server_id=None, user=None,
                    compute_type='compute'):
    '''
    Delete a deployed server

    Args:
      server:
        a server object. [Optional]
      server_id:
        an id string corresponding to server for deletion
      user:
        an authenticated user
      compute_type:
        type of compute, e.g compute or computev3
    '''
    user = user or self.user
    self._assert_preconditions(user=user)
    if not server or type(server) != Server:
      if not server_id or server_id == '':
        raise Exception('you must specify a server object or a server_id for deletion')
    
    server_id = server_id or server.id
    endpoint = user.endpoint_manager(compute_type)
    url = endpoint.fetch_url(['servers', server_id])

    logging.debug('now deleting server with id %s using url %s'%(server_id, url))
    response = requests.delete(url,
                            headers={'content-type':'application/json',
                                      'X-Auth-Token':str(self.user.token)})
    if response.status_code == requests.codes.no_content:
      logging.debug('delete_url returned status code %s'%response.status_code)
    else:
      logging.debug('response failed with status code %s'%response.status_code)
      response.raise_for_status()


  def delete_servers(self, servers=[], server_ids=[], user=None, 
                    compute_type='compute'):
    '''
    A convenience function that deletes an array of servers.

    Args:
      servers:
        a collection of server objects. [Optional]
      server_ids:
        an collection of server objects. [Optional]
      user:
        a user that has been authenticated
      compute_type:
        type of compute, e.g compute or computev3

    Note that either servers or server_ids must be specified.
    '''
    #really just a convenience function. does nothing on its own.
    for server in servers:
      self.delete_server(server=server, server_id=None, user=user,
        compute_type=compute_type)

    for server_id in server_ids:
      self.delete_server(server=None, server_id=server_id, user=user,
        compute_type=compute_type)

  def _get_url(self, url, parameters={}, success_codes=[requests.codes.ok]):
    response = requests.get(url, params=parameters,
                            headers={'content-type':'application/json',
                                     'X-Auth-Token':str(self.user.token)})
    if response.status_code in success_codes:
      logging.debug('get_url returned status code %s'%response.status_code)
      return response.json()
    else:
      logging.debug('response failed with status code %s'%response.status_code)
      response.raise_for_status()
     
  def _post_url(self, url, value):
    response = requests.post(url, data=dumps(value),
                              headers={'content-type': 'application/json',
                                        'X-Auth-Token':str(self.user.token)})
    if response.status_code == requests.codes.accepted:
      logging.debug('post_url returned status code %s'%response.status_code)
      return response.json()
    else:
      logging.debug('response failed with status code %s'%response.status_code)
      response.raise_for_status()

  def _assert_preconditions(self, user=None):
    '''
    check authentication preconditions
    '''
    if user:
      if not user.is_authenticated():
        user.authenticate()
    else:
      raise Exception("you must provide a valid user")

  def __str__(self):
    value = 'API %s:%s'%(auth_url, username)
    return value
