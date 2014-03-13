#
# Provides the models required by the compute api
#
#
class Server(object):
  '''
  An representation of an openstack server
  '''
  def __init__(self,
                admin_pass=None,
                id=None,
                access_ipv4=None,
                access_ipv6=None,
                addresses=None,
                created=None,
                flavor=None,
                host_id=None,
                image=None,
                metadata=None,
                name=None,
                progress=None,
                status=None,
                tenant_id=None,
                updated=None,
                user_id=None):
    '''
    Should be instantiated by the openstack.api class typically.

    Args:
      admin_pass: 
        provided during initial creation of a node [Optional]
      id:
        openstack provided ID of server [Required]
      access_ipv4:
        ipv4 address of this server [Optional]
      access_ipv6:
        ipv6 address of this server [Optional]
      addresses:
        private and floating ips associated with server [Optional]
      created:
        datetime of when this node was created [Optional]
      flavor:
        what is our flavor? medium, small? other.. [Optional]
      host_id:
        what openstack compute host are we hosted on [Optional]
      image:
        what image are we booting off [Optional]
      metadata:
        other user specified metadata associated with me [Optional]
      name:
        what is my user given name [Optional]
      progress:
        build progress [Optional]
      status:
        what is our current status [Optional]
      tenant_id:
        who is our tenant owner [Optional]
      updated:
        last time this info was updated [Optional]
      user_id:
        user that owns and created me [Optional]
    '''
    if admin_pass:
      self._admin_pass = admin_pass

    if not getattr(self, 'id', None):
      raise Exception("you must specify an id for a server at least")
    else:
      self._id = getattr(self, 'id')

    if access_ipv4:
      self._access_ipv4 = access_ipv4

    if access_ipv6:
      self._access_ipv6 = access_ipv6

    if addresses:
      self._addresses = addresses

    if created:
      self._created = created

    if flavor:
      self._flavor = flavor

    if host_id:
      self._host_id = host_id

    if image:
      self._image = image

    if metadata:
      self._metadata = metadata

    if name:
      self._name = name

    if progress:
      self._progress = progress

    if status:
      self._status = status

    if tenant_id:
      self._tenant_id = tenant_id

    if updated:
      self._updated = updated

    if user_id:
      self._user_id = user_id


  @classmethod
  def create_server(self, *args, **kwargs):
    if 'id' not in kwargs:
      raise Exception('you must provide an id for a server')
    return Server(id=kwargs['id'],
            admin_pass=kwargs.get('admin_pass') or kwargs.get('adminPass'),
            access_ipv4=kwargs.get('access_ipv4') or kwargs.get('accessIPv4'),
            access_ipv6=kwargs.get('access_ipv6') or kwargs.get('accessIPv6'),
            addresses=kwargs.get('addresses'),
            created=kwargs.get('created'),
            flavor=kwargs.get('flavor'),
            host_id=kwargs.get('host_id') or kwargs.get('hostId'),
            image=kwargs.get('image'),
            metadata=kwargs.get('metadata'),
            name=kwargs.get('name'),
            progress=kwargs.get('progress'),
            status=kwargs.get('status'),
            tenant_id=kwargs.get('tenantId'),
            updated=kwargs.get('updated'),
            user_id=kwargs.get('user_id') or kwargs.get('userId'))
  
  
