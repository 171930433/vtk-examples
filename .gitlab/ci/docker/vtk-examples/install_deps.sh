#!/bin/bash

apt update -y
apt upgrade -y
apt install -y git python3 cmake git xz-utils ninja-build clang gcc unzip
apt clean -y
