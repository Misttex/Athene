#!/usr/bin/env python
import pika, sys, os
import pika
from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import re
import libvirt

list_queue =["generale","creation","suppression","travail_finis","modification","OnOff","publication"]

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()



    def callback(ch, method, properties, body):
        match method.routing_key :
            case "creer":

                return print("Non louis")

            case "creation":
                import subprocess
                import uuid

                def createqcow(vm_id: str, image_name: str):
                    base_image = '/var/lib/libvirt/images/' + image_name + '.qcow2'
                    user_image = '/var/lib/libvirt/images/' + vm_id + '.qcow2'
                    create_img_result = subprocess.run(
                        ['qemu-img', 'create', '-f', 'qcow2', '-b', str(base_image), '-F', 'qcow2', str(user_image)])
                    return user_image

                def createVm(le_nom: str, memoire):
                    qcow2 = createqcow(le_nom, 'debian11')
                    le_uuid = str(uuid.uuid4())
                    conn = libvirt.open("qemu:///system")
                    xmlconfig = '<domain type="kvm"> <name>' + le_nom + '</name> <uuid>' + le_uuid + '</uuid> <metadata> <libosinfo:libosinfo xmlns:libosinfo="http://libosinfo.org/xmlns/libvirt/domain/1.0"> <libosinfo:os id="http://debian.org/debian/10"/> </libosinfo:libosinfo> </metadata> <memory>' + memoire + '</memory> <currentMemory>' + memoire + '</currentMemory> <vcpu>2</vcpu> <os> <type arch="x86_64" machine="q35">hvm</type> <boot dev="hd"/> </os> <features> <acpi/> <apic/> <vmport state="off"/> </features> <cpu mode="host-model"/> <clock offset="utc"> <timer name="rtc" tickpolicy="catchup"/> <timer name="pit" tickpolicy="delay"/> <timer name="hpet" present="no"/> </clock> <pm> <suspend-to-mem enabled="no"/> <suspend-to-disk enabled="no"/> </pm> <devices>  <disk type="file" device="disk"> <driver name="qemu" type="qcow2"/> <source file="' + qcow2 + '"/> <target dev="vda" bus="virtio"/> </disk> <disk type="file" device="cdrom"> <driver name="qemu" type="raw"/>  <target dev="sda" bus="sata"/> <readonly/> </disk> <controller type="usb" model="qemu-xhci" ports="15"/> <interface type="network"> <source network="default"/> <model type="virtio"/> </interface> <console type="pty"/> <channel type="unix"> <source mode="bind"/> <target type="virtio" name="org.qemu.guest_agent.0"/> </channel> <channel type="spicevmc"> <target type="virtio" name="com.redhat.spice.0"/> </channel> <input type="tablet" bus="usb"/> <graphics type="spice" port="-1" tlsPort="-1" autoport="yes"> <image compression="off"/> </graphics> <sound model="ich9"/> <video> <model type="qxl"/> </video> <redirdev bus="usb" type="spicevmc"/> <redirdev bus="usb" type="spicevmc"/> <memballoon model="virtio"/> <rng model="virtio"> <backend model="random">/dev/urandom</backend> </rng> </devices> </domain>'
                    dom = conn.createXML(xmlconfig, 0)
                    return dom

                le_nom = request.form['name']
                memoire = request.form['memoire']
                dom = createVm(le_nom, memoire)
                flash(le_nom + ' La machine � bien �t� cr�e', "danger")
                return print("Création de la VM %r " % dom)

            case "suppression":

                import subprocess
                le_nom = request.form['name']
                create_img_result = subprocess.run(['virsh', 'undefine', le_nom, '--remove-all-storage'])
                flash(le_nom + ' La machine � bien �t� supprim�e', "danger")
                return print("Suppréssion de la VM %r " % le_nom)

            case "travail_finis":
                return print("Création de la vm %r " % body)
            case "modification":
                return print("Création de la vm %r " % body)
            case "OnOFF":
                import time
                name = request.form['name']
                conn = libvirt.open("qemu:///system")
                vm = conn.lookupByName(name)
                if vm.isActive():
                    seconde = 0
                    while vm.isActive():
                        vm.shutdown()
                        time.sleep(1)
                        seconde += 1
                        if seconde >= 300:
                            vm.destroy()
                            msg_vm = 'close'
                            return print("Arret de la VM %r " % name)
                else:
                    vm.create()
                    msg_vm = 'open'
                    return print("Démarrage de la VM %r " % name)
                return print("Echec de l'action OnOff %r ")

            case "publication":
                return print("Création de la vm %r " % body)

    for queue in list_queue:
        channel.queue_declare(queue=queue)
        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)