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

**Get repo**

```shell
git clone https://github.com/petermat/PIPI-Detective.git
cd PIPI-Detective
```

**Install Python packages**
```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Configure Django App**
```shell
- configure GSuite credentials collector/oauth.json
```

**Set the Django app**
```shell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser


```

## Running ##

### Run local Logstash server to collect logs

Edit log path to absolute value in following file:
```shell
pipi_detective/xray/src/config/logstash.dist.yml
```
Copy to the logstash config and run:
```shell
sudo cp pipi_detective/xray/src/config/logstash.dist.yml /etc/logstash/conf.d/logstash.conf
sudo usermod -a -G logstash $USER
sudo chmod g+rwx -R /var/lib/logstash
sudo chmod g+rw -R /var/log/logstash
test:
/usr/share/logstash/bin/logstash --path.settings /etc/logstash/ 

```


### Mode: Analyze top X packages ###

Kick off celery workers if you want to use redis message queue
```shell
celery -A pipi_detective.celery.app worker --loglevel=info -c 4
```


```shell
python manage.py shell
from xray.tasks import scan_top_packages
scan_top_packages(n=100, queue=True)
```



### Mode: Analyze new packages ###

### Mode: Analyze test package ###



