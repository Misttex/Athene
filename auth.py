import logging
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import re
import libvirt

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(20)
hote = '192.168.1.82'


@app.route("/")
def index():
    return redirect("/athene/")


mysql = create_engine("mysql+pymysql://root:root@localhost/athene")


@app.route('/athene/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        db = scoped_session(sessionmaker(bind=mysql))
        account = db.execute("SELECT * FROM accounts WHERE username =:username AND password =:password",
                             {"username": username, "password": password}).fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            flash("Nom d'utilisateur / Mot de passe incorrect!", "danger")
    return render_template('auth/login.html', title="Connexion")


@app.route('/athene/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        db = scoped_session(sessionmaker(bind=mysql))
        account = db.execute("SELECT * FROM accounts WHERE username LIKE :username", {"username": username}).fetchone()

        if account:
            flash("Account already exists!", "danger")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!", "danger")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Username must contain only characters and numbers!", "danger")
        elif not username or not password or not email:
            flash("Incorrect username/password!", "danger")
        else:
            db.execute("INSERT INTO accounts(username,email,password) VALUES (:username, :email, :password)",
                       {"username": username, "email": email, "password": password})
            db.commit()
            flash("You have successfully registered!", "success")
            return redirect(url_for('login'))

    elif request.method == 'POST':
        flash("Please fill out the form!", "danger")
    return render_template('auth/register.html', title="Register")


@app.route('/athene/home')
def home():
    if 'loggedin' in session:
        '''def size_format(size_in_bytes, unit):
            if unit == 'B':
                return size_in_bytes * 1024
            elif unit == 'MB':
                return size_in_bytes / (1024)
            elif unit == 'GB':
                return size_in_bytes / (1024 * 1024)
            else:
                return size_in_bytes

        listVMPerso = []
        conn = libvirt.open("qemu:///system")
        mes_vms = conn.listDefinedDomains()
        domains = conn.listAllDomains(0)
        for domain in domains:
            dom = conn.lookupByName(domain.name())
            state, maxmem, mem, cpus, cput = dom.info()
            active = dom.isActive()
            if state == libvirt.VIR_DOMAIN_NOSTATE:
                state = 'VIR_DOMAIN_NOSTATE'
            elif state == libvirt.VIR_DOMAIN_RUNNING:
                state = 'En cours de fonctionnement'
            elif state == libvirt.VIR_DOMAIN_BLOCKED:
                state = 'Bloqué'
            elif state == libvirt.VIR_DOMAIN_PAUSED:
                state = 'En pause'
            elif state == libvirt.VIR_DOMAIN_SHUTDOWN:
                state = 'Eteinte'
            elif state == libvirt.VIR_DOMAIN_SHUTOFF:
                state = 'Eteinte'
            elif state == libvirt.VIR_DOMAIN_CRASHED:
                state = 'Crash'
            elif state == libvirt.VIR_DOMAIN_PMSUSPENDED:
                state = 'Suspendue'
            else:
                state = 'inconnu'
            tab = {
                "nom_machine": dom.name(),
                "etat": state,
                "active": active,
                "uuid": dom.UUIDString(),
                "maxmem": size_format(maxmem, 'GB'),
                "mem": size_format(mem, 'GB'),
                "nbcpus": str(cpus),
            }
            listVMPerso.append(tab)'''
        return render_template('home/home.html', listVMPerso=listVMPerso, username=session['username'], title="Home")
    return redirect(url_for('login'))


@app.route("/athene/start_stop_machine", methods=['GET', 'POST'])
def start_stop_machine():
    if 'loggedin' in session:
        '''import time
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
        else:
            vm.create()
            msg_vm = 'open'       '''
        return render_template('home/home.html', username=session['username'], title="Home")
    return redirect(url_for('login'))


@app.route("/athene/creationVm", methods=['GET', 'POST'])
def creationVm():
    if 'loggedin' in session:
        return render_template('gestion/creation.html', username=session['username'], title="Création")
    return redirect(url_for('login'))


@app.route("/athene/delete_machine", methods=['GET', 'POST'])
def delete_machine():
    import subprocess
    if 'loggedin' in session:
        le_nom = request.form['name']
        create_img_result = subprocess.run(['virsh', 'undefine', le_nom, '--remove-all-storage'])
        flash(le_nom + ' La machine à bien été supprimée', "danger")
    return redirect(url_for('login'))


@app.route("/athene/creationVmFunction", methods=['GET', 'POST'])
def creationVmFunction():
    import subprocess
    import uuid
    if 'loggedin' in session:
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
        flash(le_nom + ' La machine à bien été crée', "danger")
    return redirect(url_for('login'))


@app.route('/athene/profile')
def profile():
    if 'loggedin' in session:
        return render_template('auth/profile.html', username=session['username'], title="Profile")
    return redirect(url_for('login'))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True, host=hote, port="1500")