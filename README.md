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
**
>>> import openstack
>>> help(openstack)
**


Notes
=========
It is being tested with Openstack Havana release and should work for python
2.6+ environments
