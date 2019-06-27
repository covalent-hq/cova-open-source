#!/bin/bash
# wget https://raw.githubusercontent.com/covalent-hq/bigchaindb-setup/master/setup_bigchaindb.sh && sudo bash setup_bigchaindb.sh

# ref: https://askubuntu.com/a/30157/8698
if ! [ $(id -u) = 0 ]; then
   echo "The script need to be run as root." >&2
   echo "USAGE: sudo bash cova_clave_install.sh" >&2
   exit 1
fi

if [ $SUDO_USER ]; then
    real_user=$SUDO_USER
else
    real_user=$(whoami)
fi

echo "Hello! "$real_user

# sudo adduser cova
# sudo usermod -aG sudo cova

# firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 26656/tcp
sudo ufw allow 9984/tcp
sudo ufw -f enable 

# upgrade system
sudo apt update -y
sudo apt full-upgrade -y

# install essentials + bdb
sudo apt install -y python3-pip libssl-dev
sudo pip3 install bigchaindb==2.0.0b9
sudo apt install -y mongodb
sudo apt install -y unzip
sudo apt install -y nginx
sudo apt install -y monit

# fix mongodb: symlink
sudo service mongodb stop
mkdir /home/cova/.mongodb
sudo mv /var/lib/mongodb /home/cova/.mongodb
sudo ln -s /home/cova/.mongodb /var/lib/mongodb
sudo chown mongodb:mongodb /home/cova/.mongodb
sudo service mongodb start
sudo service mongodb status


sudo -u $real_user wget https://github.com/tendermint/tendermint/releases/download/v0.22.8/tendermint_0.22.8_linux_amd64.zip
sudo -u $real_user unzip tendermint_0.22.8_linux_amd64.zip
sudo -u $real_user rm tendermint_0.22.8_linux_amd64.zip
sudo mv tendermint /usr/local/bin

# setup bdb and tendermint
sudo -u $real_user bigchaindb configure

# CHANGE CONFIG TO
# 0.0.0.0:9984

# init tendermint
sudo -u $real_user tendermint init

sudo -u $real_user cat /home/cova/.tendermint/config/priv_validator.json
sudo -u $real_user tendermint show_node_id

sudo -u $real_user systemctl status mongodb




