#!/bin/bash
# Generate API documents from the latest source code

script_dir=`dirname $0`
cd ${script_dir}/..

pip install -U pdoc3
rm -rf docs/api-docs
pdoc slack_bolt --html -o docs/api-docs
open docs/api-docs/slack_bolt/index.html
