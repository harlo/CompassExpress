#! /bin/bash

sudo start service ssh
sudo cron -f &

./startup.sh
tail -f /dev/null