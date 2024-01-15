#!/bin/bash
apt update -y
apt install -y python3 python3-venv git openssh-client rsync
python3 -m venv venv/vtk-examples-web
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cp "$SSH_KNOWN_HOSTS" ~/.ssh/known_hosts
chmod 644 ~/.ssh/known_hosts
chmod 400 $GH_KEY
git config --global user.email kwrobot+vtk-examples@kitware.com
git config --global user.name "Kitware Robot"
