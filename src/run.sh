#! /bin/bash

sudo start service ssh
sudo cron -f &

cd ~/CompassFrontend && ./startup.sh
cd ~/CompassAnnex && ./startup.sh
./tail.sh