zabuza
======
A python openstack REST API client. Why? Because there is no easy to use
central python api client for openstack like boto for AWS.

This is a work in progress therefore suggestions, contributions are very
welcome.
===========
Installing
===========
Simply clone this repository and run the setup.py to install. You could
optionally run 'setup.py test' to run included tests. It expects the following
variables defined in your environment: 

**ZABUZA_TOKEN_URL**: Your keystone admin token url where tokens are generated

**ZABUZA_USERNAME**

**ZABUZA_PASSWORD**

**ZABUZA_TENANT_NAME**

Optionally, you could choose not to include have these variables available and
pass them during invocation of the Openstack api module.

=========
Notes
=========
It is being tested with Openstack Havana release and should work for python
2.6+ environments
