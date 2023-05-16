#!/bin/bash

script_dir=`dirname $0`
cd ${script_dir}/..
rm -rf ./slack_bolt.egg-info

pip install -U pip && \
  pip install twine wheel && \
  rm -rf dist/ build/ slack_bolt.egg-info/ && \
  python setup.py sdist bdist_wheel && \
  twine check dist/*