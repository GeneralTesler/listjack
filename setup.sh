#!/bin/bash
apt-get install xvfb
apt-get install libffi-dev
apt-get install libfuzzy-dev
apt-get install attr
wget https://github.com/mozilla/geckodriver/releases/download/v0.17.0/geckodriver-v0.17.0-linux64.tar.gz
tar -xvf geckodriver-v0.17.0-linux64.tar.gz
rm geckodriver-v0.17.0-linux64.tar.gz
mv geckodriver /usr/sbin
ln -s /usr/sbin/geckodriver /usr/bin/geckodriver
pip install -r requirements.txt