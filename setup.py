# from distutils.core import setup
import os
import re
from sys import version

from setuptools import setup


if version < '2.2.3':
    print 'Versio requires python 2.6 or newer'
    exit(-1)

VERSION_REGEX = r'__version__\s*=\s*[\'\"](\S+)[\'\"]'


def get_project_version():
    """
    Get the version from __init__.py with a line: /^__version__\s*=\s*(\S+)/
    If it doesn't exist try to load it from the VERSION.txt file.
    If still no joy, then return '0.0.0'

    :returns: the version string
    :rtype: str
    """

    # trying __init__.py first
    try:
        file_name = os.path.join(os.getcwd(), 'versio', '__init__.py')
        with open(file_name, 'r') as inFile:
            for line in inFile.readlines():
                match = re.match(VERSION_REGEX, line)
                if match:
                    return match.group(1)
    except IOError:
        pass

    # no joy, so try getting the version from a VERSION.txt file.
    try:
        file_name = os.path.join(os.getcwd(), 'versio', 'VERSION.txt')
        with open(file_name, 'r') as inFile:
            return inFile.read().strip()
    except IOError:
        pass

    # no joy again, so return default
    return '0.0.0'


setup(
    name='Versio',
    version=get_project_version(),
    author='royw',
    author_email='roy@wright.org',
    url='http://github.com/royw/versio',
    packages=['versio'],
    package_dir={'': '.'},
    package_data={'versio': ['*.txt', '*.js', '*.html', '*.css'],
                  'docs': ['*'],
                  'tests': ['*'],
                  'herringlib': ['*'],
                  '': ['*.txt', '*.rc', 'herringfile', '*.in']},
    license='license.txt',
    description='Version manipulation library.',
    long_description=open('README.txt').read(),
    install_requires=[
        # "argparse",
        # "mako"
        # "Foo >= 1.2.3"
    ],

    # entry_points={
    #     'console_scripts': ['versio = versio.versio_app:main']
    # }
)
