__author__ = 'Williams-Sonoma'
__version__ = '0.3.1'

METADATA = dict(
  name = 'zabuza',
  version = __version__,
  py_modules = ['openstack', 'keystone'],
  author = __author__,
  author_email = 'contact@chookah.org',
  description = 'A python wrapper around Openstack API',
  url = 'https://github.com/okoye/zabuza',
  keywords = 'openstack api',
)

SETUPTOOLS_METADATA = dict(
  install_requires = ['setuptools', 'simplejson', 'requests', 'python-dateutil'],
  include_package_data = True,
  test_suite = 'tests',
)


def main():
  try:
    import setuptools
    METADATA.update(SETUPTOOLS_METADATA)
    setuptools.setup(**METADATA)
  except ImportError:
    import distutils.core
    distutils.core.setup(**METADATA)

if __name__ == '__main__':
  main()
