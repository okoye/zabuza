
class User(object):
  '''
  An abstract representation of an openstack user.
  Handles authentication of current user.
  '''
  def __init__(self, auth_url, username=None, password=None, token=None,
    tenant_name=None):
    self.username = username
    self.password = password
    self.token = token #TODO: an actual token object
    self.tenant_name = tenant_name

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
