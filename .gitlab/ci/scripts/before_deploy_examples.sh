#!/bin/bash
apt update -y
apt install -y rsync openssh-client
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cp "$SSH_KNOWN_HOSTS" ~/.ssh/known_hosts
chmod 644 ~/.ssh/known_hosts
chmod 400 $RSYNC_KEY
