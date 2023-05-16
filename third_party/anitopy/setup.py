from pathlib import Path
from setuptools import setup
import sys


LONG_DESCRIPTION = Path('README.rst').read_text()
REQUIRED_PACKAGES = []
if sys.version_info < (3, 4):
    REQUIRED_PACKAGES.append('enum34')

setup(
    name='anitopy',
    packages=['anitopy'],
    version='2.2.0rc2',
    description='An anime video filename parser',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    author='Igor Cescon de Moura',
    author_email='igorcesconm@gmail.com',
    url='https://github.com/igorcmoura/anitopy',
    python_requires='>=2.7',
    install_requires=REQUIRED_PACKAGES,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
