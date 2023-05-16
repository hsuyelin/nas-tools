#!/bin/bash
rm -rf vendor && mkdir -p vendor/slack_bolt && cp -pr ../../slack_bolt/* vendor/slack_bolt/
pip install python-lambda -U
lambda deploy \
  --config-file aws_lambda_config.yaml \
  --requirements requirements.txt