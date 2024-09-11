#!/bin/bash
# Variables
SPLUNK_PASSWORD='password'  # Change this!
SPLUNK_USER='admin'
SPLUNK_DEB_URL='https://download.splunk.com/products/splunk/releases/9.2.1/linux/splunk-9.2.1-78803f08aabb-linux-2.6-amd64.deb'
# Download and Install Splunk

if ! test -f /vagrant/splunk.deb; then
  echo "Splunk does not exist. Downloading..."
  wget -q -O /vagrant/splunk.deb $SPLUNK_DEB_URL
else
  echo "Splunk deb file found."
fi

sudo dpkg -i /vagrant/splunk.deb
# Configure Splunk to start at boot and set admin password
/opt/splunk/bin/splunk enable boot-start --accept-license --answer-yes --no-prompt --seed-passwd $SPLUNK_PASSWORD
# Start Splunk
/opt/splunk/bin/splunk start --accept-license --answer-yes --no-prompt --seed-passwd $SPLUNK_PASSWORD
# Automatically add a monitor for the /opt/splunk-logs directory
/opt/splunk/bin/splunk add monitor /opt/splunk-logs -index main -auth $SPLUNK_USER:$SPLUNK_PASSWORD
# Restart Splunk to apply the configuration
/opt/splunk/bin/splunk restart
echo "Splunk installation and configuration completed."