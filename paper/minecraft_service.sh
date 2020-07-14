#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd )"
cd $DIR

# Starts the minecraft server script with the user 'minecraft'
sudo -u minecraft ./minecraft_server.sh