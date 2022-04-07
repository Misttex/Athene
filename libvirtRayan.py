import subprocess
import uuid
import libvirt

def createqcow(vm_id: str, image_name: str):
    base_image = '/var/lib/libvirt/images/'+image_name+ '.qcow2'
    user_image = '/var/lib/libvirt/images/'+vm_id+ '.qcow2'
    create_img_result = subprocess.run(['qemu-img', 'create', '-f', 'qcow2','-b', str(base_image), '-F', 'qcow2', str(user_image)])
    return user_image

def createVm(le_nom: str):
     qcow2 = createqcow(le_nom, 'debian11')
     le_uuid = str(uuid.uuid4())
     conn = libvirt.open("qemu:///system")
     xmlconfig = '<domain type="kvm"> <name>'+le_nom+'</name> <uuid>'+le_uuid+'</uuid> <metadata> <libosinfo:libosinfo xmlns:libosinfo="http://libosinfo.org/xmlns/libvirt/domain/1.0"> <libosinfo:os id="http://debian.org/debian/10"/> </libosinfo:libosinfo> </metadata> <memory>1048576</memory> <currentMemory>1048576</currentMemory> <vcpu>2</vcpu> <os> <type arch="x86_64" machine="q35">hvm</type> <boot dev="hd"/> </os> <features> <acpi/> <apic/> <vmport state="off"/> </features> <cpu mode="host-model"/> <clock offset="utc"> <timer name="rtc" tickpolicy="catchup"/> <timer name="pit" tickpolicy="delay"/> <timer name="hpet" present="no"/> </clock> <pm> <suspend-to-mem enabled="no"/> <suspend-to-disk enabled="no"/> </pm> <devices>  <disk type="file" device="disk"> <driver name="qemu" type="qcow2"/> <source file="'+qcow2+'"/> <target dev="vda" bus="virtio"/> </disk> <disk type="file" device="cdrom"> <driver name="qemu" type="raw"/>  <target dev="sda" bus="sata"/> <readonly/> </disk> <controller type="usb" model="qemu-xhci" ports="15"/> <interface type="network"> <source network="default"/> <model type="virtio"/> </interface> <console type="pty"/> <channel type="unix"> <source mode="bind"/> <target type="virtio" name="org.qemu.guest_agent.0"/> </channel> <channel type="spicevmc"> <target type="virtio" name="com.redhat.spice.0"/> </channel> <input type="tablet" bus="usb"/> <graphics type="spice" port="-1" tlsPort="-1" autoport="yes"> <image compression="off"/> </graphics> <sound model="ich9"/> <video> <model type="qxl"/> </video> <redirdev bus="usb" type="spicevmc"/> <redirdev bus="usb" type="spicevmc"/> <memballoon model="virtio"/> <rng model="virtio"> <backend model="random">/dev/urandom</backend> </rng> </devices> </domain>'
     dom = conn.createXML(xmlconfig, 0)
     return dom

le_nom = 'rayan'
dom= createVm(le_nom)