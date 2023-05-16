#!/bin/bash
# Run all the tests or a single test
# all: ./scripts/install_all_and_run_tests.sh
# single: ./scripts/install_all_and_run_tests.sh tests/scenario_tests/test_app.py

script_dir=`dirname $0`
cd ${script_dir}/..
rm -rf ./slack_bolt.egg-info
# The package causes a conflict with moto
pip uninstall python-lambda

test_target="$1"

pip install -e .

if [[ $test_target != "" ]]
then
  # To fix: Using legacy 'setup.py install' for greenlet, since package 'wheel' is not installed.
  pip install -U wheel && \
    pip install -e ".[testing]" && \
    pip install -e ".[adapter]" && \
    pip install -e ".[adapter_testing]" && \
    # To avoid errors due to the old versions of click forced by Chalice
    pip install -U pip click && \
    black slack_bolt/ tests/ && \
    pytest $1
else
  # To fix: Using legacy 'setup.py install' for greenlet, since package 'wheel' is not installed.
  pip install -U wheel && \
    pip install -e ".[testing]" && \
    pip install -e ".[adapter]" && \
    pip install -e ".[adapter_testing]" && \
    # To avoid errors due to the old versions of click forced by Chalice
    pip install -U pip click && \
    black slack_bolt/ tests/ && \
    pytest && \
    pip install -U pytype && \
    pytype slack_bolt/
fi
