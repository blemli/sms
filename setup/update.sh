set -e
name=$(basename $(git rev-parse --show-toplevel))
cd /opt/$name
git restore setup/*
git stash
git fetch && git reset --hard origin/main
sudo chmod +x setup/*.sh
. setup/install.sh
#. setup/install-$name-admin.sh
sudo service avahi-daemon restart
sudo systemctl restart caddy
