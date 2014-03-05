import unittest
import logging
from os import environ
from openstack import User, Api

class UserTest(unittest.TestCase):
  def setUp(self):
    #assumes credentials are available in environment
    url = environ.get('KEYSTONE_URL') or environ.get('KEYSTONE_ADMIN_URL')
    username = environ.get('OS_USERNAME')
    password = environ.get('OS_PASSWORD')
    tenant = environ.get('TENANT')
    token = environ.get('TOKEN')
    self.good_user = User(url, username=username, password=password,
      tenant_name=tenant)
    self.tokenized_user = User(url, token=token)
    self.no_cred_user = User(url)
    self.bad_cred_user = User(url, username='nonexistentuser',
      password='1337haxor')

  def test__instantiation(self):
    self.assertTrue(isinstance(User, self.good_user))
    self.assertTrue(isinstance(User, self.tokenized_user))
    self.assertTrue(isinstance(User, self.no_cred_user))
    self.assertTrue(isinstance(User, self.bad_cred_user))

  def test__can_authenticate(self):
    #self.assertTrue(self.good_user.authenticate())
    pass

class ApiTest(unittest.TestCase):
  pass


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  unittest.main()
