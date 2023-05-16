#!/bin/bash

pip uninstall -y slack-bolt && \
  pip freeze | grep -v "^-e" | xargs pip uninstall -y
