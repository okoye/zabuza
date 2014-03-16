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
                user_id=None,
                availability_zone=None,
                security_group_name=None,
                **kwargs):
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
        what image [id or url] are we booting off [Optional]
      metadata:
        key value metadata with max size 255 bytes [Optional]
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
      availability_zone:
        what availability zone does this server belong to [Optional]
      security_group_name:
        security group currently applied to this server [Optional]
    '''
    if admin_pass:
      self._admin_pass = admin_pass

    if not kwargs.get('id'):
      raise Exception("you must specify an id for a server at least")
    else:
      self._id = kwargs.get('id')
    
    self._access_ipv4 = access_ipv4 or None
    self._access_ipv6 = access_ipv6 or None
    self._addresses = addresses or None
    self._created = created or None
    self._flavor = flavor or None
    self._host_id = host_id or None
    self._image = image or None
    self._metadata = metadata or None
    self._name = name or None
    self._progress = progress or None
    self._status = status or None
    self._tenant_id = tenant_id or None
    self._updated = updated or None
    self._user_id = user_id or None
    self._security_group_name = security_group_name or None
    self._availability_zone = availability_zone or None

  @classmethod
  def create_server(self, *args, **kwargs):
    if not kwargs.get('id'):
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
            user_id=kwargs.get('user_id') or kwargs.get('userId'),
            availability_zone=kwargs.get('availability_zone') or kwargs.get('availabilityZone'),
            security_group_name=kwargs.get('security_group_name') or kwargs.get('securityGroupName'))

  @classmethod
  def create_server_for_deployment(self, image, flavor, name, **kwargs):
    '''
    convenience function for creating __and__ ensuring basic info for
    creating a new server is provided

    Args:
      image:
        an id or url reference to image [Required]
      flavor:
        an id or url reference to flavor [Required]
      name:
        a string name of this box [Required]
      metadata:
        dict of relevant metadata [Optional]
      availability_zone:
        a string representing az [Optional]
      user_data:
        specific user data for cloud init base64 encoded [Optional]
      security_group:
        what is my security group [Optional]
    '''
    assert image is not None
    assert flavor is not None
    assert name is not None

    return Server(id=None,
              image=image,
              flavor=flavor,
              name=name,
              metadata=kwargs.get('metadata'),
              availability_zone=kwargs.get('availability_zone'),
              user_data=kwargs.get('user_data'),
              security_group=kwargs.get('security_group'))

  def get_id(self):
    return self._id

  id = property(get_id, doc='server id')

  def get_admin_pass(self):
    return self._admin_pass

  def set_admin_pass(self, value):
    self._admin_pass = value

  admin_pass = property(get_admin_pass, set_admin_pass,
                        doc='autogenerated admin password')
  
  def get_ipv4(self):
    return self._access_ipv4

  def set_ipv4(self, value):
    self._access_ipv4 = value

  access_ipv4 = property(get_ipv4, set_ipv4,
                          doc='ipv4 address of this server')

  def get_ipv6(self):
    return self._access_ipv6

  def set_ipv6(self, value):
    self._access_ipv6 = value

  access_ipv6 = property(get_ipv6, set_ipv6,
                          doc='ipv6 address of this server')

  def get_addresses(self):
    return self._addresses

  def set_addresses(self, value):
    self._addresses = value

  addresses = property(get_addresses, set_addresses,
                      doc='addresses of this server')

  def get_created(self):
    return self._created

  def set_created(self, value):
    self._created = value

  created = property(get_created, set_created, 
                    doc='datetime of server creation')

  def get_flavor(self):
    return self._flavor

  def set_flavor(self, value):
    self._flavor = value

  flavor = property(get_flavor, set_flavor,
                    doc='flavor of this server')

  def get_host_id(self):
    return self._host_id

  def set_host_id(self, value):
    self._host_id = value

  host_id = property(get_host_id, set_host_id,
                    doc='underlying compute host id')

  def get_image(self):
    return self._image

  def set_image(self, value):
    self._image = value

  image = property(get_image, set_image,
                  doc='image this server has spawned from')

  def get_metadata(self):
    return self._metadata

  def set_metadata(self, value):
    self._metadata = value

  metadata = property(get_metadata, set_metadata,
                      doc='custom metadata of this node')

  def get_name(self):
    return self._name
  
  def set_name(self, value):
    self._name = value

  name = property(get_name, set_name,
                  doc='name of this server')

  def get_status(self):
    return self._status

  def set_status(self, value):
    self._status = value

  status = property(get_status, set_status,
                    doc='current status/state of this server')

  def get_progress(self):
    return self._progress

  def set_progress(self, value):
    self._progress = value

  progress = property(get_progress, set_progress,
                      doc='build progress of this server')

  def get_tenant_id(self):
    return self._tenant_id

  def set_tenant_id(self, value):
    self._tenant_id = value

  tenant_id = property(get_tenant_id, set_tenant_id,
                        doc='tenant id this server belongs to')

  def get_updated(self):
    return self._updated

  def set_updated(self, value):
    self._updated = value

  updated = property(get_updated, set_updated,
                    doc='datetime object this server was updated')

  def get_user_id(self):
    return self._user_id

  def set_user_id(self, value):
    self._user_id = value

  user_id = property(get_user_id, set_user_id,
                    doc='user id of owner of this server')

  def get_availability_zone(self):
    return self._availability_zone

  def set_availability_zone(self, value):
    self._availability_zone = value

  availability_zone = property(get_availability_zone, set_availability_zone,
                              doc='string representing availability zone')

  def get_security_group_name(self):
    return self._security_group_name

  def set_security_group_name(self, value):
    self._security_group_name = value

  security_group_name = property(get_security_group_name,
                                  set_security_group_name,
                                  doc='string representing the security group name')
