#!/usr/bin/env python
# Example provisioning API usage script.  (C) DataStax, 2015.  All Rights Reserved
#
# Needs these OS environmental variables pre-defined: lcm_server, cassandra_default_password, opscenter_session (optional), dse_ver (optional), cluster_name (optional)
# command line parameter with node IP/DC in the following format:
# public_IP:private_IP:DC_name:node_number

import os
import sys
import requests
import json
import threading
import argparse
import subprocess
import webbrowser

# Configurable args
ap = argparse.ArgumentParser()
ap.add_argument("-ip", "--public_ip", required=True,
	help="public IP address of the target server")
ap.add_argument("-k", "--ssh_key", required=True,
	help="private key to be used")
ap.add_argument("-u", "--user", required=True,
	help="username for the server")
args = vars(ap.parse_args())

server_ip = args["public_ip"]
ssh_key = args["ssh_key"]
username = args["user"]

repo_user = os.environ.get('academy_user').strip()
repo_pass = os.environ.get('academy_pass').strip()
download_token = os.environ.get('academy_token').strip()

#SSH into the OpsCenter/LCM server, install the JDK, install OpsCenter
bashCommand = 'ssh -o StrictHostKeyChecking=accept-new -i '+ ssh_key+ ' '+ username+'@'+server_ip+' \'sudo apt-get install -y python software-properties-common; \
sudo apt-add-repository -y ppa:webupd8team/java; \
sudo apt-get update; \
echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | sudo debconf-set-selections; \
sudo apt-get install -y oracle-java8-installer; \
echo "deb https://'+repo_user+':'+download_token+'@debian.datastax.com/enterprise \
stable main" | sudo tee -a /etc/apt/sources.list.d/datastax.sources.list; \
curl -L https://debian.datastax.com/debian/repo_key | sudo apt-key add - ; \
sudo apt-get update; sudo apt-get install dse-full;\
\' 2>/dev/null'

output = subprocess.check_output(['bash','-c', bashCommand])
