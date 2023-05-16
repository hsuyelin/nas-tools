#!/bin/bash

script_dir=`dirname $0`
cd ${script_dir}/../docs
gem install bundler
bundle install
rm -rf _site/
bundle exec jekyll serve -It
