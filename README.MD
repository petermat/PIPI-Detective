# PIPI Detective #

A Django application designed to scrutinize the behavior of Python PIPI packages. 
Each package is installed within a virtual environment and monitored using custom OSQuery eBPF filters.

Operation Modes:
- Top 10K Package Analysis: Gather logs to establish a baseline of normal behavior.
- New Package Analysis: Investigate for potential malicious indicators.
- Test Package Analysis: Develop and refine detection mechanisms.



## Installation ##

This manual is specifically for Ubuntu 24.04, but it is also compatible with most POSIX-compliant operating systems.

**Instal Vagrant and Redis**
```shell
sudo apt install -y git vagrant build-essential
sudo apt install -y redis-server

```


**Install Virtualization Provider: Virtualbox or KVM**


A) Virtualbox 


B) KVM
```shell
sudo apt install -y qemu-kvm virt-manager libvirt-daemon-system virtinst libvirt-clients bridge-utils libvirt-dev
vagrant plugin install vagrant-libvirt
sudo usermod -a -G libvirt ${USER}
sudo usermod -aG kvm $USER 
```

Change range of vagrant-libvirt network to accommodate lange number of hosts
```shell
virsh net-destroy vagrant-libvirt
virsh net-undefine vagrant-libvirt
virsh net-create pipi_detective/xray/src/config/vagrant-libvirt.xml
virsh net-autostart vagrant-libvirt
```


**Get repo**

Clone repo and edit settings.
```shell
git clone https://github.com/petermat/PIPI-Detective.git
cd PIPI-Detective
cp pipi_detective/config/dev.dist.py pipi_detective/config/dev.py
nano pipi_detective/config/dev.py  
```

**Install Python packages**
```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Configure Django App**

Configure GSuite credentials collector/oauth.json
```shell
cp collector/oauth.dist.json collector/oauth.json
nano collector/oauth.json
```

**Set the Django app**
```shell
python manage.py makemigrations xray colector
python manage.py migrate
python manage.py createsuperuser
```

## Running ##

### Run local Logstash server to collect logs

Edit log path to absolute value in following file:
```shell
cp pipi_detective/xray/src/config/logstash.dist.yml pipi_detective/xray/src/config/logstash.yml
nsno pipi_detective/xray/src/config/logstash.yml
```
Copy to the logstash config and run:
```shell
sudo cp pipi_detective/xray/src/config/logstash.yml /etc/logstash/conf.d/logstash.conf
sudo usermod -a -G logstash $USER
sudo chmod g+rwx -R /var/lib/logstash
sudo chmod g+rw -R /var/log/logstash
test:
/usr/share/logstash/bin/logstash --path.settings /etc/logstash/ 

```


### Mode: Analyze top X packages ###

Kick off celery workers if you want to use redis message queue
```shell
celery -A pipi_detective.celery.app worker --loglevel=info -c 10
```

```shell
python manage.py shell
from xray.tasks import scan_top_packages
scan_top_packages(n=100, queue=True)
```



### Mode: Analyze new packages ###

### Mode: Analyze test package ###



