#! /bin/bash

git config --global user.name "compass"
git config --global user.email "compass@j3m.info"

cd ~/CompassAnnex && ./setup.sh /home/compass/unveillance.compass.annex.json
source ~/.bash_profile
cd ~/CompassFrontend && ./setup.sh /home/compass/unveillance.compass.frontend.json