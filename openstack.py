import requests
import logging
from random import choice
from traceback import format_exc
from datetime import datetime
from dateutil.parser import parse as dateparser
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
      if aname not in self._catalog:
        self._catalog[aname] = []
      for endpoint in service['endpoints']:
        self._catalog[aname].append(Endpoint(name=aname, type=atype, **endpoint))

  def get_endpoint_for(self, service_name, region=None):
    '''
    Supported service_names include:
      nova, neutron, cinder, glance, swift, keystone, ec2
    '''
    if service_name not in self._catalog:
      raise ValueError('Unrecognized service endpoint specified')
    selector = lambda endpoints: choice(endpoints)
    if not region:
      return selector(self._catalog[service_name])
    else:
      return filter(lambda x: x.region == region, self._catalog[service_name])

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
    self._catalog = ServiceCatalog(**user_info)

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
      assert isinstance(User, user)
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
  
  def create_server(self, server, user_data=None, user=None):
    '''
    Create a new server. The main required parameter is a server.

    Args:
      server:
        a server object. recommended to create with the 
      user_data:
        base64 encoded configuration info and scripts to use upon launch
      user:
        a user object that has been authenticated
    '''
    user = user or self.user
    self._assert_preconditions(user=user)
    endpoint = self.user.endpoint_manager('nova')
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
    if server.security_group:
      parameters['server']['security_group'] = server.security_group
    if user_data:
      parameters['server']['user_data'] = user_data

    logging.debug('now creating server %s at url %s'%(parameters, url))
    json_data = self._post_url(url, parameters)
    server.update_properties(**json_data['server'])


  def _post_url(self, url, value):
    return {'id':'test', 'adminPass':'chookah'}

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
    #TODO: what is an appropriate representation of an API object?
    pass
