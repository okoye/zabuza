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
    Returns a boolean indicating if authentication was successful or not
    '''
    raise NotImplementedError

    
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

  def verify_credentials(self):
    '''
    Have we specified valid credentials which we can perform openstack
    operations with

    returns a boolean indicate if verification was successful or not
    '''
    raise NotImplementedError
