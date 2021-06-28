# coding=utf-8
import os
import re
from setuptools import setup
import sys


if sys.version_info < (2, 6):
    print('Versio requires python 2.6 or newer')
    exit(-1)

VERSION_REGEX = r'__version__\s*=\s*[\'\"](\S+)[\'\"]'


def get_project_version():
    r"""
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

    # no joy again, so return default
    return '0.0.0'


# all versions of python
required_imports = [
]

# libraries that have been moved into python
print("Python (%s)" % sys.version)
if sys.version_info < (3, 1):
    required_imports.extend([
        'ordereddict',  # new in py31
    ])

if sys.version_info < (3, 2):
    required_imports.extend([
        "argparse",  # new in py32
    ])

setup(
    name='Versio',
    version=get_project_version(),
    author='Roy Wright',
    author_email='roy@wright.org',
    url='https://github.com/royw/Versio',
    download_url='https://github.com/royw/Versio/archive/versio-{ver}.tar.gz'.format(ver=get_project_version()),
    packages=['versio'],
    package_dir={'': '.'},
    package_data={'': ['*.rst', '*.txt', '*.rc', '*.in']},
    license='license.txt',
    description='Version manipulation library.',
    long_description=open('README.rst').read(),
    keywords=['version', 'PEP 440'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    install_requires=required_imports,
)
