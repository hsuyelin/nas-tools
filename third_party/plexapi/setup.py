#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Install PlexAPI
"""
from pkg_resources import parse_requirements
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from plexapi import const

# Get README.rst contents
readme = open('README.rst', 'r').read()

# Get requirements
with open('requirements.txt') as handle:
    requirements = [str(req) for req in parse_requirements(handle)]

setup(
    name='PlexAPI',
    version=const.__version__,
    description='Python bindings for the Plex API.',
    author='Michael Shepanski',
    author_email='michael.shepanski@gmail.com',
    url='https://github.com/pkkid/python-plexapi',
    packages=['plexapi'],
    install_requires=requirements,
    python_requires='>=3.7',
    long_description=readme,
    keywords=['plex', 'api'],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
    ]
)
