

__author__ = 'Williams-Sonoma'
__version__ = '0.3.2'

METADATA = dict(
  name = 'zabuza',
  version = __version__,
  py_modules = ['openstack'],
  author = __author__,
  author_email = 'contact@chookah.org',
  description = 'A python wrapper around Openstack API',
  url = 'https://github.com/okoye/zabuza',
  keywords = 'openstack api',
)

def main():
  try:
    from setuptools import setup, find_packages
    SETUPTOOLS_METADATA = dict(
      install_requires = ['setuptools', 'simplejson', 'requests', 'python-dateutil'],
      include_package_data = True,
      package_dir={'':'zabuza'},
      packages=find_packages(where='zabuza'),
      test_suite = 'tests',
    )
    METADATA.update(SETUPTOOLS_METADATA)
    setup(**METADATA)
  except ImportError:
    import distutils.core
    distutils.core.setup(**METADATA)


if __name__ == '__main__':
  main()
