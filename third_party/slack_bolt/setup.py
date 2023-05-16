#!/usr/bin/env python
import os
import sys

import setuptools

here = os.path.abspath(os.path.dirname(__file__))

__version__ = None
exec(open(f"{here}/slack_bolt/version.py").read())

with open(f"{here}/README.md", "r") as fh:
    long_description = fh.read()

test_dependencies = [
    "pytest>=6.2.5,<7",
    "pytest-cov>=3,<4",
    "Flask-Sockets>=0.2,<1",  # TODO: This module is not yet Flask 2.x compatible
    "Werkzeug>=1,<2",  # TODO: Flask-Sockets is not yet compatible with Flask 2.x
    "itsdangerous==2.0.1",  # TODO: Flask-Sockets is not yet compatible with Flask 2.x
    "Jinja2==3.0.3",  # https://github.com/pallets/flask/issues/4494
    "black==22.8.0",  # Until we drop Python 3.6 support, we have to stay with this version
    "click<=8.0.4",  # black is affected by https://github.com/pallets/click/issues/2225
]

adapter_test_dependencies = [
    "moto>=3,<4",  # For AWS tests
    "docker>=5,<6",  # Used by moto
    "boddle>=0.2,<0.3",  # For Bottle app tests
    "Flask>=1,<2",  # TODO: Flask-Sockets is not yet compatible with Flask 2.x
    "Werkzeug>=1,<2",  # TODO: Flask-Sockets is not yet compatible with Flask 2.x
    "sanic-testing>=0.7" if sys.version_info.minor > 6 else "",
    "requests>=2,<3",  # For Starlette's TestClient
]

async_test_dependencies = test_dependencies + [
    "pytest-asyncio>=0.18.2,<1",  # for async
    "aiohttp>=3,<4",  # for async
]

setuptools.setup(
    name="slack_bolt",
    version=__version__,
    license="MIT",
    author="Slack Technologies, LLC",
    author_email="opensource@slack.com",
    description="The Bolt Framework for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/slackapi/bolt-python",
    packages=setuptools.find_packages(
        exclude=[
            "examples",
            "integration_tests",
            "tests",
            "tests.*",
        ]
    ),
    include_package_data=True,  # MANIFEST.in
    install_requires=[
        "slack_sdk>=3.21.1,<4",
    ],
    setup_requires=["pytest-runner==5.2"],
    tests_require=async_test_dependencies,
    test_suite="tests",
    extras_require={
        # pip install -e ".[async]"
        "async": [
            # async features heavily depends on aiohttp
            "aiohttp>=3,<4",
            # Socket Mode 3rd party implementation
            "websockets>=10,<11" if sys.version_info.minor > 6 else "websockets>=8,<10",
        ],
        # pip install -e ".[adapter]"
        # NOTE: any of async ones requires pip install -e ".[async]" too
        "adapter": [
            # used only under src/slack_bolt/adapter
            "boto3<=2",
            "bottle>=0.12,<1",
            "chalice>=1.28,<2" if sys.version_info.minor > 6 else "chalice<=1.27.3",
            "CherryPy>=18,<19",
            "Django>=3,<5",
            "falcon>=3.1.1,<4" if sys.version_info.minor >= 11 else "falcon>=2,<4",
            "fastapi>=0.70.0,<1",
            "Flask>=1,<3",
            "Werkzeug>=2,<3",
            "pyramid>=1,<3",
            "sanic>=22,<23" if sys.version_info.minor > 6 else "sanic>=20,<21",
            "starlette>=0.14,<1",
            "tornado>=6,<7",
            # server
            "uvicorn<1",  # The oldest version can vary among Python runtime versions
            "gunicorn>=20,<21",
            # Socket Mode 3rd party implementation
            # Note: 1.2.2 has a regression (https://github.com/websocket-client/websocket-client/issues/769)
            "websocket_client>=1.2.3,<2",
        ],
        # pip install -e ".[testing_without_asyncio]"
        "testing_without_asyncio": test_dependencies,
        # pip install -e ".[testing]"
        "testing": async_test_dependencies,
        # pip install -e ".[adapter_testing]"
        "adapter_testing": adapter_test_dependencies,
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
