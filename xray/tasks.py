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


# todo: functions:
# learning - going over top packages
# test - lead evil_package
# discovery - run with new packages

from collector.models import Pipipackage


### MANUAL BULK ACTION
def scan_top_packages(n=30, queue=True):
    print("À")
    list_of_top_packages = Pipipackage.objects.filter(logs_collected__isnull=True).order_by('-top_rating').values_list(
        'id', 'name')[:n]
    # list_of_top_packages_obj = Pipipackage.objects.all().order_by('-top_rating')[:100]
    for pckg_tp in list_of_top_packages:
        if queue:
        # creating redis task
            _run_vm_vagrant.delay(package_name=pckg_tp[1], packageobj_id=pckg_tp[0])
        else:
            _run_vm_vagrant(package_name=pckg_tp[1], packageobj_id=pckg_tp[0])
        print("Running: ", pckg_tp[1])

### MANUAL BULK ACTION
def scan_new_packages(self):
    # todo
    pass

### Test
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
    print("DEBUG about to UP: ",package_name)
    os_env = os.environ.copy()
    os_env['HOSTNAME'] = re.sub(r"[^a-zA-Z-\.\d]+", '', package_name.split("@")[0])
    os_env['HOSTNAME'] += f"-{uuid.uuid4().hex.upper()[0:4]}"
    os_env['PACKAGE_NAME_INSTALL'] = package_name

    # evil_package = evil-package@git+https://github.com/petermat/evil-package
    os_env['PACKAGE_NAME_IMPORT'] = re.sub(r'^python[-_]', '', package_name).split("@")[0].replace("-","_")
    #os_env['VAGRANT_LOG'] = 'debug' not working?
    v.env = os_env
    #v.up(vm_name='ubuntu') #vm_name=XX, provider=libvirt|virtualbox
    v.up(vm_name=os_env['HOSTNAME'], provider=str(settings.VAGRANT_PROVIDER or "virtualbox"))
    print("DEBUG UP ok.")
    print(v.user_hostname_port(vm_name=os_env['HOSTNAME']))

    env.hosts = [v.user_hostname_port(vm_name=os_env['HOSTNAME'])]
    env.key_filename = v.keyfile(vm_name=os_env['HOSTNAME'])
    env.disable_known_hosts = True  # useful for when the vagrant box ip changes.

    # verify that logs are synced

    folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'src', 'logs', os_env['HOSTNAME'])
    # todo: required -> vagrant plugin install vagrant-scp

    v._run_vagrant_command(["vagrant", "global-status"])
    print(f"DEBUG: About to execute: vagrant scp {os_env['HOSTNAME']}:/var/log/osquery {folder_path}")
    v._run_vagrant_command(["vagrant", "scp", f"{os_env['HOSTNAME']}:/var/log/osquery {folder_path}"])


    """ obsolete - logs are pulled by Django - no need for this check anymore
    logs_uploaded = False
    while not logs_uploaded:
        time.sleep(5)
        latest_mtime = None
        # Loop through each file in the specified folder
        for filename in os.listdir(folder_path):
            # Construct the full path to the file
            file_path = os.path.join(folder_path, filename)
            # Skip if it's a directory
            if os.path.isdir(file_path):
                continue
            # Get the last modification time of the file
            mtime = os.path.getmtime(file_path)
            # Update the latest_mtime if this file is newer
            if latest_mtime is None or mtime > latest_mtime:
                latest_mtime = mtime

            print("DEBUG: found log file {}, timestamp: {}".format(file_path,mtime))

        # Convert the latest modification time to a datetime object
        if latest_mtime is not None:
            latest_date = datetime.fromtimestamp(latest_mtime)

            print("Waiting for logs before teardown. Timestamp: {}".format(latest_mtime))
            # Check if the latest_date is junker than 20 seconds compared to the current time

            if latest_date and datetime.now() - latest_date < timedelta(seconds=5):
                logs_uploaded = True
            else:
                print("Waiting for logs after teardown. Diff: {}".format(datetime.now() - latest_date))

        else:
            print("Warning: Log files latest_date is empty ")
            time.sleep(5)
    """

    # TODO Get logs from guest machine
    # idea1: vagrant function?
    # idea2: ssh?
    # idea3: shared folder?

    try:
        v.destroy(vm_name=os_env['HOSTNAME'])
        print("DEBUG: destroying vm {}".format(package_name))
    except Exception as e:
        print("DEBUG: Teardown of VM '{}' failed: {}".format(package_name, e))

    finally:
        if packageobj_id:
            pckg_obj = Pipipackage.objects.get(id=packageobj_id)
            pckg_obj.logs_collected = timezone.now()
            pckg_obj.save()



""" # libvirt version - obsolete
def _run_vm(self, package_name):

    name = package_name

    conn = libvirt.open()
    if conn is None:
        print('Failed to connect to the hypervisor')
        return
    #if conn.lookupByName(name):
    #    print(f'Virtual machine {name} already exists')

    try:
        # Check if the virtual machine already exists
        if conn.lookupByName(name):
            print(f'Virtual machine {name} already exists')

    except:
        # Create the virtual machine
        xmlconfig = f'''
                <domain type='kvm'>
                    <name>{name}</name>
                    <memory unit='MiB'>1024</memory>
                    <vcpu placement='static'>1</vcpu>
                    <os>
                        <type arch='x86_64' machine='pc-i440fx-2.12'>hvm</type>
                        <boot dev='hd'/>
                    </os>
                    <devices>
                        <disk type='file' device='disk'>
                            <driver name='qemu' type='qcow2'/>
                            <source file='/var/lib/libvirt/images/disk_image.qcow2'/>
                            <target dev='vda' bus='virtio'/>
                            <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
                        </disk>
                        <interface type='network'>
                            <mac address='52:54:00:aa:bb:cc'/>
                            <source network='default'/>
                            <model type='virtio'/>
                            <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
                        </interface>
                    </devices>
                </domain>
            '''

        conn.createXML(xmlconfig, 0)
        print(f'Virtual machine {name} created successfully')

        #except libvirt.libvirtError as e:
            #print(f'Failed to create virtual machine: {str(e)}')
        conn.close()

# libvirt version - obsolete
def _get_vm_list(self):
    # create list of VM and IPs for ssh connection
    conn = libvirt.open()
    if conn is None:
        print('Failed to connect to the hypervisor')
        return None

    out_list = list()
    domains = conn.listDomainsID()

    if not domains:
        print('No local domains')
    for domain_id in domains:
        #print("Domain 0: id %d running %s" % (domain.ID(), domain.OSType()))
        #print(domain.info())

        this_vm = conn.lookupById(domain_id)
        # Grab the MAC Address from the XML definition
        #     using a regex, which may appear multiple times in the XML
        mac_addresses = re.search(r"<mac address='([A-Z0-9:]+)'", vm.XMLDesc(0)).groups()

        for mac_address in mac_addresses:
            # Now, use subprocess to lookup that macaddress in the
            #      ARP tables of the host.
            process = subprocess.Popen(['/sbin/arp', '-a'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            process.wait()  # Wait for it to finish with the command
            for line in process.stdout:
                if mac_address in line:
                    ip_address = re.search(r'(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})', line)
                    print('VM {0} with MAC Address {1} is using IP {2}'.format(
                        this_vm.name(), mac_address, ip_address.groups(0)[0]))
                    out_list.append([this_vm.name(), mac_address, ip_address.groups(0)[0]])
                else:
                    # Unknown IP Address from the ARP tables! Handle this somehow...
                    pass
    return out_list

#def ttemp(self):
"""






