import requests
import logging
from traceback import format_exc
try:
  import json
except ImportError:
  import simplejson as json

class PasswordCredential(object):
  '''
  A representation of the password credentials object required
  by keystone
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
    return json.dumps({'username': self.username,
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
    self.token = token #TODO: an actual token object
    self.tenant_name = tenant_name
    self.auth_url = auth_url

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

  def is_authenticated(self):
    '''
    Verified that we have and can authenticate against the openstack API.
    Note that all operations done against the API will use your token supplied
    not your username/password pair. This routine also validates that our token
    is still valid
    '''
    raise NotImplementedError

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
    logging.debug('authenticate data: %s'%json.dumps(post_data))
    response = requests.post(self.auth_url, data=json.dumps(post_data))
    if response.status_code == requests.codes.ok:
      #create appropriate objects from returned response
      print response
    else:
      response.raise_for_status()


  def _can_authenticate(self):
    '''
    Verify that all the parameters necessary for authentication has been made
    present:
      username, password / token, tenant_name
    '''
    if not self.token:
      if not self.credentials.is_valid():
        return False

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

  def __str__(self):
    raise NotImplementedError
