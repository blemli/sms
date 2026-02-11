set -e
name=$(basename $(git rev-parse --show-toplevel))
cd /opt/$name
git restore setup/*
git stash
git pull
sudo chmod +x setup/*.sh
. setup/install.sh
#. setup/install-$name-admin.sh
sudo service avahi-daemon restart
sudo systemctl restart caddy
