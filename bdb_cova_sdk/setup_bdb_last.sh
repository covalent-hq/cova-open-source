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
bash bigchaindb-monit-config
monit -d 1
monit summary


