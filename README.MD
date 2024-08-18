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
sudo apt install vagrant
sudo apt install redis-server

```


**Install Virtualization Provider: Virtualbox or KVM**


A) Virtualbox 


B) KVM
```shell
sudo apt install -y qemu-kvm virt-manager libvirt-daemon-system virtinst libvirt-clients bridge-utils
```

**Get repo**

```shell
git clone ...
cd ...
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
python manage.py createsuperuser
python manage.py makemigrations
python manage.py migrate

```

## Running ##

### Mode: Analyze top X packages ###

Run ... or manually execute Google BigQuery for csv export

```sql
SELECT file.project ,COUNT(*) as download_count
        FROM `bigquery-public-data.pypi.file_downloads`
        WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY file.project
        ORDER BY download_count DESC
        LIMIT 10000
```


### Mode: Analyze new packages ###

### Mode: Analyze test package ###



