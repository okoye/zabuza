import unittest
import logging
from os import environ
from openstack import User, Api, PasswordCredential
try:
  import json
except ImportError:
  import simplejson as json

class PasswordCredentials(unittest.TestCase):
  def setUp(self):
    self.cred = PasswordCredential()
    self.valid_cred = PasswordCredential(username='foo', password='bar')

  def test__credentials_properties(self):
    valid_cred = PasswordCredential(username='foo', password='bar')
    self.assertTrue(hasattr(self.cred, 'username'))
    self.assertTrue(hasattr(self.cred, 'password'))
    self.assertEquals(valid_cred.username, 'foo')
    self.assertEquals(valid_cred.password, 'bar')

  def test__credentials_serialization(self):
    cred = PasswordCredential(username='foo', password='bar')
    self.assertEquals(cred.json, json.dumps({'username':'foo', 'password':'bar'}))
    self.assertEquals(cred.python_dict, {'username':'foo', 'password':'bar'})

class UserTest(unittest.TestCase):
  def setUp(self):
    #assumes credentials are available in environment
    url = environ.get('ZABUZA_AUTH_URL')
    username = environ.get('ZABUZA_USERNAME')
    password = environ.get('ZABUZA_PASSWORD')
    tenant = environ.get('ZABUZA_TENANT_NAME')
    token = environ.get('TOKEN') or None
    self.good_user = User(url, username=username, password=password,
      tenant_name=tenant)
    self.tokenized_user = User(url, token=token)
    self.no_cred_user = User(url)
    self.bad_cred_user = User(url, username='nonexistentuser',
      password='1337haxor')

  def test__instantiation(self):
    self.assertTrue(isinstance(self.good_user, User))
    self.assertTrue(isinstance(self.tokenized_user, User))
    self.assertTrue(isinstance(self.no_cred_user, User))
    self.assertTrue(isinstance(self.bad_cred_user, User))

  def test__no_credentials_in_env(self):
    self.assertRaises(AttributeError, self.no_cred_user.authenticate)

  def test__can_authenticate(self):
    self.assertTrue(self.good_user.authenticate())

class ApiTest(unittest.TestCase):
  pass


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  unittest.main()
