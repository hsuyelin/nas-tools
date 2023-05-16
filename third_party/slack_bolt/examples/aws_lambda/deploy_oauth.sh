#!/bin/bash
rm -rf slack_bolt && mkdir slack_bolt && cp -pr ../../slack_bolt/* slack_bolt/
pip install python-lambda -U
lambda deploy \
  --config-file aws_lambda_oauth_config.yaml \
  --requirements requirements_oauth.txt
