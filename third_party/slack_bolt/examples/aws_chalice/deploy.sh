#!/bin/bash

# configure aws credentials properly
pip install -U chalice click boto3
pip install -r requirements.txt
# edit .chalice/config.json
rm -rf vendor && mkdir -p vendor/slack_bolt && cp -pr ../../slack_bolt/* vendor/slack_bolt/
chalice deploy
