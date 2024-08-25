#import libvirt
import os
from datetime import datetime, timedelta
from django.utils import timezone
import re
import time
import subprocess
import vagrant
from fabric.api import env, execute, task, run
from celery import shared_task
from django.conf import settings


from collector.models import Pipipackage
from xray.models import Snapshot


import subprocess
import logging
import sys
import psutil
import os
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



### MAIN ACTION
def scan_top_packages(n=30 , queue=True):

    list_of_top_packages = Pipipackage.objects.filter(logs_collected__isnull=True).order_by('-top_rating').values_list(
        'id', 'name')[:n]
    # list_of_top_packages_obj = Pipipackage.objects.all().order_by('-top_rating')[:100]
    if not list_of_top_packages:
        print("WARNING: list_of_top_packages empty - run:")
        print("from collector.tasks import load_top_from_csv")
        print("load_top_from_csv()")

    for pckg_tp in list_of_top_packages:
        if queue:
        # creating redis task
            _run_vm_vagrant.delay(package_name=pckg_tp[1], packageobj_id=pckg_tp[0])
        else:
            _run_vm_vagrant(package_name=pckg_tp[1], packageobj_id=pckg_tp[0])
        print("Running: ", pckg_tp[1])

### MAIN BULK ACTION
def scan_new_packages(self):
    # todo
    pass

### TEST ACTION
def scan_evil_package(queue=False, pckg_id=None):
    #self._run_vm_vagrant(package_name="evil_package")
    if queue:
        _run_vm_vagrant.delay(package_name="evil_package@git+https://github.com/petermat/evil_package")
    else:
        _run_vm_vagrant(package_name="evil_package@git+https://github.com/petermat/evil_package")


@shared_task
def _run_vm_vagrant(package_name, packageobj_id=None):

    import uuid
    vagrantfile_path = os.path.join(os.path.dirname(__file__), 'src')
    log_cm = vagrant.make_file_cm('deployment.log')

    v = vagrant.Vagrant(root=vagrantfile_path, quiet_stdout=False) #out_cm=log_cm, err_cm=log_cm)
    print("DEBUG about to spin: ",package_name)
    os_env = os.environ.copy()
    os_env['HOSTNAME'] = re.sub(r"[^a-zA-Z-\.\d]+", '', package_name.split("@")[0])
    os_env['HOSTNAME'] += f"-{uuid.uuid4().hex.upper()[0:4]}"
    os_env['PACKAGE_NAME_INSTALL'] = package_name

    # evil_package = evil-package@git+https://github.com/petermat/evil-package
    os_env['PACKAGE_NAME_IMPORT'] = re.sub(r'^python[-_]', '', package_name).split("@")[0].replace("-","_")
    #os_env['VAGRANT_LOG'] = 'debug' not working?
    v.env = os_env
    #v.up(vm_name='ubuntu') #vm_name=XX, provider=libvirt|virtualbox

    try:
        v.up(vm_name=os_env['HOSTNAME'], provider=str(settings.VAGRANT_PROVIDER or "virtualbox"))
    except Exception as e:
        print(f"ERROR: {os_env['HOSTNAME']}", e)
        if packageobj_id:
            sn_obj, created = Snapshot.objects.update_or_create(
                filename=None,
                failure=str(e),
                pipipackage=Pipipackage.objects.get(id=packageobj_id))
        time.sleep(10)
    else:
        print(v.user_hostname_port(vm_name=os_env['HOSTNAME']))

        env.hosts = [v.user_hostname_port(vm_name=os_env['HOSTNAME'])]
        env.key_filename = v.keyfile(vm_name=os_env['HOSTNAME'])
        env.disable_known_hosts = True  # useful for when the vagrant box ip changes.

        # verify that logs are synced
        log_filename = os_env['HOSTNAME']+datetime.now().strftime("-%Y-%m-%d")+".log"
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'src', 'logs', log_filename)

        while not os.path.exists(file_path):
            print("Log file not found ", file_path, ". Waiting 5 sec")
            time.sleep(5)

        while time.time() - os.path.getmtime(file_path) < 5:
            print("Log file too fresh, waiting 5 sec")
            time.sleep(5)


        if packageobj_id:

            sn_obj, created = Snapshot.objects.update_or_create(
                    filename=log_filename,
                    #ruleset=dict(),
                    #findings=dict(),
                    pipipackage=Pipipackage.objects.get(id=packageobj_id))

            pckg_obj = Pipipackage.objects.get(id=packageobj_id)
            pckg_obj.logs_collected = timezone.now()
            pckg_obj.save()


    try:
        v.destroy(vm_name=os_env['HOSTNAME'])
        print("DEBUG: destroying vm {}".format(package_name))
    except Exception as e:
        print("DEBUG: Teardown of VM '{}' failed: {}".format(package_name, e))


    try:
        # virsh undefine guest1 --remove-all-storage
        command = ['virsh', 'undefine', os_env['HOSTNAME'], '--remove-all-storage']
        # Run the command in the background
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except Exception as e:
        pass





