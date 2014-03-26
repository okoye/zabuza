import unittest
import logging
from os import environ
from traceback import format_exc
from src.zabuza.openstack import User, Api, PasswordCredential, Token, Endpoint
from src.zabuza.openstack import ServiceCatalog
from src.zabuza.services.compute import Server
try:
  import json
except ImportError:
  import simplejson as json

class PasswordCredentialTest(unittest.TestCase):
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
    url = environ.get('ZABUZA_TOKEN_URL')
    username = environ.get('ZABUZA_USERNAME')
    password = environ.get('ZABUZA_PASSWORD')
    tenant = environ.get('ZABUZA_TENANT_NAME')
    token = Token(id='foo', expires='2014-03-10T14:47:21.383780',
                  issued_at='2014-03-10T14:47:21.383780', tenant={})
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
    try:
      self.good_user.authenticate()
    except Exception as ex:
      msg = str(ex)
      tb = format_exc()
      self.fail('%s: %s'%(msg, tb))
    else:
      self.assertTrue(True) #noop really

class TokenTest(unittest.TestCase):
  
  def test__missing_instantiation_parameters(self):
    self.assertRaises(KeyError, Token)

  def test__token_properties(self):
    token = Token(id='foo', expires='2014-03-10T14:47:21.383780',
                  issued_at='2014-03-10T14:47:21.383780', tenant={})
    self.assertTrue(hasattr(token, 'id'))
    self.assertTrue(hasattr(token, 'expires'))
    self.assertTrue(hasattr(token, 'issued_at'))
    self.assertTrue(hasattr(token, 'tenant'))

class EndpointTest(unittest.TestCase):
  
  def setUp(self):
    self.id = 'mah-id'
    self.admin_url = 'http://foo.bar'
    self.region = 'mars'
    self.internal_url = 'http://bar.foo'
    self.public_url = 'http://bar.foo.vim'
    self.type = 'compute'
    self.name = 'nova'

  def test__no_attributes(self):
    self.assertRaises(KeyError, Endpoint)

  def test__instance_attributes_and_instantiation(self):
    endpoint = Endpoint(admin_url=self.admin_url,
                        region=self.region,
                        internal_url=self.internal_url,
                        id=self.id,
                        public_url=self.public_url,
                        type=self.type,
                        name=self.name)
    camel_endpoints = Endpoint(adminURL=self.admin_url,
                                internalURL=self.internal_url,
                                id=self.id,
                                publicURL=self.public_url,
                                type=self.type,
                                name=self.name)
    self.assertEquals(getattr(endpoint, '_admin_url'), self.admin_url)
    self.assertEquals(getattr(endpoint, '_region'), self.region)
    self.assertEquals(getattr(endpoint, '_internal_url'), self.internal_url)
    self.assertEquals(getattr(endpoint, '_id'), self.id)
    self.assertEquals(getattr(endpoint, '_public_url'), self.public_url)
    self.assertEquals(getattr(endpoint, '_type'), self.type)
    self.assertEquals(getattr(endpoint, '_name'), self.name)
    self.assertTrue(hasattr(camel_endpoints, '_admin_url'))
    self.assertTrue(hasattr(camel_endpoints, '_internal_url'))
    self.assertTrue(hasattr(camel_endpoints, '_public_url'))

class ServiceCatalogTest(unittest.TestCase):

  def setUp(self):
    self.id = 'yoh-id'
    self.admin_url = 'http://razz.tazz'
    self.region = 'jupiter'
    self.internal_url = 'http://tazz.razz'
    self.public_url = 'http://tazz.razz.shazz'
    self.type = 'network'
    self.name = 'neutron'
    self.sc_template = ServiceCatalog(service_catalog=[
      {
        'endpoints': [
          {
            'adminURL': self.admin_url,
            'region': self.region,
            'internalURL': self.internal_url,
            'id': self.id,
            'publicURL': self.public_url
          }
        ],
        'endpoints_link': [],
        'type': self.type,
        'name': self.name
      }
    ])
    self.sc = self.sc_template

  def test__attributes(self):
    self.assertTrue(hasattr(self.sc_template, '_catalog'))
    self.assertTrue(isinstance(self.sc.get_endpoint_for(self.type), Endpoint))
    self.assertRaises(ValueError, self.sc.get_endpoint_for, 'nothing')

class ServerTest(unittest.TestCase):

  def setUp(self):
    self.id = 'some id'

  def test__no_id_instantiation(self):
    self.assertRaises(Exception, Server, tenant_id='1234')
    self.assertRaises(Exception, Server.create_server)

  def test__proper_instantiation(self):
    server = Server(id=1234)
    self.assertTrue(hasattr(server, 'id'))
    server = Server.create_server(**{'id':'1234'})
    self.assertTrue(hasattr(server, 'id'))
    data = '''
    {
    "server": {
        "accessIPv4": "",
        "accessIPv6": "",
        "addresses": {
            "private": [
                {
                    "addr": "192.168.0.3",
                    "version": 4
                }
            ]
        },
        "created": "2012-08-20T21:11:09Z",
        "flavor": {
            "id": "1",
            "links": [
                {
                    "href": "http://openstack.example.com/openstack/flavors/1",
                    "rel": "bookmark"
                }
            ]
        },
        "hostId": "65201c14a29663e06d0748e561207d998b343e1d164bfa0aafa9c45d",
        "id": "893c7791-f1df-4c3d-8383-3caae9656c62",
        "image": {
            "id": "70a599e0-31e7-49b7-b260-868f441e862b",
            "links": [
                {
                    "href": "http://openstack.example.com/openstack/images/70a599e0-31e7-49b7-b260-868f441e862b",
                    "rel": "bookmark"
                }
            ]
        },
        "links": [
            {
                "href": "http://openstack.example.com/v2/openstack/servers/893c7791-f1df-4c3d-8383-3caae9656c62",
                "rel": "self"
            },
            {
                "href": "http://openstack.example.com/openstack/servers/893c7791-f1df-4c3d-8383-3caae9656c62",
                "rel": "bookmark"
            }
        ],
        "metadata": {
            "My Server Name": "Apache1"
        },
        "name": "new-server-test",
        "progress": 0,
        "status": "ACTIVE",
        "tenant_id": "openstack",
        "updated": "2012-08-20T21:11:09Z",
        "user_id": "fake"
    }
    } 
    '''
    formatted_data = json.loads(data)
    server = Server.create_server(**formatted_data['server']) 
    self.assertEquals(server.access_ipv4, formatted_data['server']['access_ipv4'])
    self.assertEquals(server.host_id, formatted_data['server']['hostId'])

  def test__deploy_server_instantiation(self):
    server = Server.create_server_for_deployment('foo', 'bar', 'vaz')
    self.assertTrue(isinstance(server, Server))

class ApiTest(unittest.TestCase):

  def setUp(self):
    url = environ.get('ZABUZA_TOKEN_URL')
    username = environ.get('ZABUZA_USERNAME')
    password = environ.get('ZABUZA_PASSWORD')
    tenant = environ.get('ZABUZA_TENANT_NAME')
    self.api = Api(url, username=username, password=password, tenant_name=tenant)

  def test__create_server(self):
    image = environ.get('ZABUZA_TEST_IMAGE_ID')
    flavor = environ.get('ZABUZA_TEST_FLAVOR_ID') or 1
    name = 'zabuza_test_create_server'
    server = Server.create_server_for_deployment(image, flavor, name)
    self.api.create_server(server)
    self.assertTrue(hasattr(server, 'admin_pass'))
    self.assertTrue(server.admin_pass is not None)

  def test__create_server_with_userdata(self):
    image = environ.get('ZABUZA_TEST_IMAGE_ID')
    flavor = environ.get('ZABUZA_TEST_FLAVOR_ID') or 1
    name = 'zabuza_test_create_server_with_userdata'
    server = Server.create_server_for_deployment(image, flavor, name)
    self.api.create_server(server, user_data_file='/tmp/foo.sh')
    self.assertTrue(hasattr(server, 'admin_pass'))
    self.assertTrue(server.admin_pass is not None)

  def test__get_server_detail(self):
    self.assertRaises(Exception, self.api.get_server_detail) #server or server_id must be specified
    server = Server.create_server_for_deployment(image, flavor, name)
    self.api.create_server(server)
    self.assertEquals(self.api.get_server_detail(server), server)

  def test__get_servers_detail(self):
    #TODO: more tests on this.
    pass

if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  unittest.main()
