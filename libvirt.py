import libvirt
import re
import subprocess
import uuid

def size_format(b):
    if b < 1000:
              return '%i' % b + 'B'
    elif 1000 <= b < 1000000:
        return '%.1f' % float(b/1000) + 'KB'
    elif 1000000 <= b < 1000000000:
        return '%.1f' % float(b/1000000) + 'MB'
    elif 1000000000 <= b < 1000000000000:
        return '%.1f' % float(b/1000000000) + 'GB'
    elif 1000000000000 <= b:
        return '%.1f' % float(b/1000000000000) + 'TB'

conn = libvirt.open("qemu:///system")
mes_vms = conn.listDefinedDomains()
domains = conn.listAllDomains(0)
for domain in domains:
    dom = conn.lookupByName(domain.name())
    state, maxmem, mem, cpus, cput = dom.info()
    if state == libvirt.VIR_DOMAIN_NOSTATE:
        state = 'VIR_DOMAIN_NOSTATE'
    elif state == libvirt.VIR_DOMAIN_RUNNING:       
         state = 'VIR_DOMAIN_RUNNING'
    elif state == libvirt.VIR_DOMAIN_BLOCKED:      
         state = 'VIR_DOMAIN_BLOCKED'
    elif state == libvirt.VIR_DOMAIN_PAUSED:      
         state = 'VIR_DOMAIN_PAUSED'
    elif state == libvirt.VIR_DOMAIN_SHUTDOWN:      
         state = 'VIR_DOMAIN_SHUTDOWN'
    elif state == libvirt.VIR_DOMAIN_SHUTOFF:      
         state = 'VIR_DOMAIN_SHUTOFF'
    elif state == libvirt.VIR_DOMAIN_CRASHED:      
         state = 'VIR_DOMAIN_CRASHED'
    elif state == libvirt.VIR_DOMAIN_PMSUSPENDED:      
         state = 'VIR_DOMAIN_PMSUSPENDED'
    else:
        state = 'inconnu'
    active = dom.isActive()
    maxmem = size_format(maxmem) 
    
    mem = size_format(mem) 
    persistent = dom.isPersistent()
    print('persistent ? ' + str(persistent))
    print('active ? ' + str(active))
    print('The state is ' + str(state))
    print('The max memory is ' + str(maxmem))
    print('The memory is ' + str(mem))
    print('The number of cpus is ' + str(cpus))
    print('The cpu time is ' + str(cput))



  
    
    le_uuid = str(uuid.uuid4())
    le_nom = 'test2'
    xmlconfig = '<domain type="kvm"> <name>'+le_nom+'</name> <uuid>'+le_uuid+'</uuid> <metadata> <libosinfo:libosinfo xmlns:libosinfo="http://libosinfo.org/xmlns/libvirt/domain/1.0"> <libosinfo:os id="http://debian.org/debian/10"/> </libosinfo:libosinfo> </metadata> <memory>1048576</memory> <currentMemory>1048576</currentMemory> <vcpu>2</vcpu> <os> <type arch="x86_64" machine="q35">hvm</type> <boot dev="hd"/> </os> <features> <acpi/> <apic/> <vmport state="off"/> </features> <cpu mode="host-model"/> <clock offset="utc"> <timer name="rtc" tickpolicy="catchup"/> <timer name="pit" tickpolicy="delay"/> <timer name="hpet" present="no"/> </clock> <pm> <suspend-to-mem enabled="no"/> <suspend-to-disk enabled="no"/> </pm> <devices> <emulator>/usr/bin/qemu-system-x86_64</emulator> <disk type="file" device="disk"> <driver name="qemu" type="qcow2"/> <source file="/var/lib/libvirt/images/debian7server.qcow2"/> <target dev="vda" bus="virtio"/> </disk> <disk type="file" device="cdrom"> <driver name="qemu" type="raw"/> <source file="/home/rayan/vm/iso/debian-11.2.0-amd64-netinst.iso"/> <target dev="sda" bus="sata"/> <readonly/> </disk> <controller type="usb" model="qemu-xhci" ports="15"/> <interface type="network"> <source network="default"/> <mac address="52:54:00:ac:b4:d8"/> <model type="virtio"/> </interface> <console type="pty"/> <channel type="unix"> <source mode="bind"/> <target type="virtio" name="org.qemu.guest_agent.0"/> </channel> <channel type="spicevmc"> <target type="virtio" name="com.redhat.spice.0"/> </channel> <input type="tablet" bus="usb"/> <graphics type="spice" port="-1" tlsPort="-1" autoport="yes"> <image compression="off"/> </graphics> <sound model="ich9"/> <video> <model type="qxl"/> </video> <redirdev bus="usb" type="spicevmc"/> <redirdev bus="usb" type="spicevmc"/> <memballoon model="virtio"/> <rng model="virtio"> <backend model="random">/dev/urandom</backend> </rng> </devices> </domain>'
    print(xmlconfig)
    dom = conn.createXML(xmlconfig, 0)
    print(dom,dom.name())
