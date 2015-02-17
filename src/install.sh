#! /bin/bash

git config --global user.name "compass"
git config --global user.email "compass@j3m.info"

cd ~/CompassAnnex && ./setup.sh ~/unveillance.compass.annex.json
cd ~/CompassFrontend && ./setup.sh ~/unveillance.compass.frontend.json