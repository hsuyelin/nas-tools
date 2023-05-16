#!/bin/bash
# ./scripts/run_pytype.sh

script_dir=$(dirname $0)
cd ${script_dir}/.. && \
  pip install -e ".[async]" && \
  pip install -e ".[adapter]" && \
  pip install "pytype==2022.12.15" && \
  pytype slack_bolt/
