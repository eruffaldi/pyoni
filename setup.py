from distutils.core import setup
import sys
from setuptools import  find_packages,Extension

is_windows = sys.platform.startswith('win')

if is_windows:
	q = ['-static-libgcc']
else:
	q = []
modulexndec = Extension('xndec.libxndec', extra_compile_args=['--std=c++11'],extra_link_args=q,sources = ['extern/xndec/xn16zdec.cpp'])
moduleany = Extension('anyregistration.libanyregistration', include_dirs=['.','/opt/local/include/eigen3'] ,extra_compile_args=['--std=c++11'],extra_link_args=q, sources = ['extern/anyregistration/anyregistration.cpp'])

setup(
  name = 'pyoni',
  version = '0.6.1',
  install_requires = ['pypng','pillow'],
  description = 'Python OpenNI ONI tool',
  author = 'Emanuele Ruffaldi',
  author_email = 'emanuele ruffaldi',
  url = 'https://github.com/eruffaldi/pyoni', # use the URL to the github repo
  keywords = ['rgbd', 'tool', 'oni','openni'], # arbitrary keywords
  classifiers = [],
  scripts = ['src/pyonitool.py'],
  packages=find_packages('src'), 
  package_dir = {'':'src'},
  ext_modules = [moduleany] #removed modulexndec
)
