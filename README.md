zabuza
======
A python openstack REST API client. Why? Because there is no easy to use
central python api client for openstack like boto for AWS.

This is a work in progress therefore suggestions, contributions are very
welcome .

Installing
===========
Simply clone this repository and run the setup.py to install. You could
optionally run 'setup.py test' to run included tests. It expects the following
variables defined in your environment: 

**ZABUZA_TOKEN_URL**: Your keystone admin token url where tokens are generated

**ZABUZA_USERNAME**: A keystone account preferably an administrator

**ZABUZA_PASSWORD**: Password for the provided keystone account

**ZABUZA_TENANT_NAME**: Tenant this account belongs to

Optionally, you could choose not to include have these variables available and
pass them during invocation of the Openstack api module.

Using
=====
Zabuza provides python client for Openstack APIs (keystone, nova, at this time)

To get more information about a specific module e.g the openstack module:

>>> from zabuza import openstack; help(openstack)

To use the API we need to instantiate an 'Api' object with some authentication
parameters passed in. E.g

>>> openstack.Api('http://keystone:35357/v2.0/tokens',username='foo', password='bar')

you could also pass in a token object or a user object that was stored as a
pickled object (remember to deserialize it before passing in)

>>> openstack.Api('http://keystone:35357/v2.0/tokens', token=mytoken,
>>>               tenant_name='demo')
>>> openstack.Api('http://keystone:35357/v2.0/tokens', user=auser,
>>>               tenant_name='demo')

If you have an existing token you could just construct your own token object:

>>> token = openstack.Token(id='token-id',
>>>                         expires='2014-03-10T14:47:21.383780',
>>>                         issued_at='2014-03-10T14:47:21.383780',
>>>                         tenant='your-tenant-name')

and then pass the token parameter as shown above.

After authenticating with the Api, you can now execute the api methods or just
simply validate your credentials by calling the verify_credentials.

For more information on supported api methods call:
>>> help(openstack.Api)



Notes
=========
It is being tested with Openstack Havana release and should work for python
2.6+ environments

Versioning in this module follows the semantic versioning scheme. More
information can be found here:
http://semver.org/
