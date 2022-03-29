# -*-coding:Latin-1 -*
import os
import logging
import uuid
import requests
from requests_oauth2.services import GoogleClient
from requests_oauth2 import OAuth2BearerToken
from flask import Flask, request, redirect, session, render_template
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import logout_user
import pika
import libvirt

host_projet = 'localhost'
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(20)
blueprint = make_google_blueprint()
app.register_blueprint(blueprint, url_prefix="/accueil/")



google_auth = GoogleClient(
    client_id=("554229061086-np1qvffgq6gi1f6njg99qkeqt4h2gaut"
               ".apps.googleusercontent.com"),
    client_secret="XqTsoS6DXq-W0KgTqvQISBOM",
    redirect_uri="http://"+host_projet+":5000/google/oauth2callback",

)

#Par default si aucune route est spï¿½cifier envoie vers la route /Logout
@app.route("/")
def index():
    return redirect("/logout")


#Route de dï¿½connection
#Supprimer le token google
@app.route("/logout")
def logout():
    if session.get("access_token"):
        token = session["access_token"]
        resp = google.post(
            "https://accounts.google.com/o/oauth2/revoke",
            params={"token": token},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        del token
        return render_template("login.html")
    else:
        return render_template("login.html")

#Route pour afficher la page d'accueil
@app.route("/accueil/")
def google_index():
    if not session.get("access_token"):
        return redirect("/logout")
    with requests.Session() as s:
        s.auth = OAuth2BearerToken(session["access_token"])
        r = s.get("https://www.googleapis.com/plus/v1/people/me")
    r.raise_for_status()
    data = r.json()

    listVMPerso = []
    conn = libvirt.open("qemu:///system")
    mes_vms = conn.listDefinedDomains()
    domains = conn.listAllDomains(0)
    for domain in domains:
        dom = conn.lookupByName(domain.name())
        state, maxmem, mem, cpus, cput = dom.info()
        if state == libvirt.VIR_DOMAIN_NOSTATE:
            state = 'VIR_DOMAIN_NOSTATE'
        elif state == libvirt.VIR_DOMAIN_RUNNING:
            state = '2'
        elif state == libvirt.VIR_DOMAIN_BLOCKED:
            state = '0'
        elif state == libvirt.VIR_DOMAIN_PAUSED:
            state = '1'
        elif state == libvirt.VIR_DOMAIN_SHUTDOWN:
            state = '0'
        elif state == libvirt.VIR_DOMAIN_SHUTOFF:
            state = '0'
        elif state == libvirt.VIR_DOMAIN_CRASHED:
            state = '0'
        elif state == libvirt.VIR_DOMAIN_PMSUSPENDED:
            state = '1'
        else:
            state = 'inconnu'
        tab = {
            "nom_machine": dom.name(),
            "etat": state,
            "uuid": dom.UUIDString(),
        }
        listVMPerso.append(tab)

    return render_template("index.html",
                           name=" Bonjour, {}".format(data["displayName"]),
                           url=format(data["image"]["url"]),
                           listVMPerso=listVMPerso)

#Verification sur l'utilisateur est connecter
@app.route("/google/oauth2callback")
def google_oauth2callback():
    code = request.args.get("code")
    error = request.args.get("error")
    if error:
        return "error :( {!r}".format(error)
    if not code:
        return redirect(google_auth.authorize_url(
            scope=["profile", "email"],
            response_type="code",
        ))
    usertoken = google_auth.get_token(
        code=code,
        grant_type="authorization_code",
    )
    session["access_token"] = usertoken.get("access_token")
    return redirect("/accueil/")



#Route pour afficher la page de crï¿½ation VM
@app.route("/newVM")
def newVM():
    if not session.get("access_token"):
        return redirect("/logout")
    with requests.Session() as s:
        s.auth = OAuth2BearerToken(session["access_token"])
        r = s.get("https://www.googleapis.com/plus/v1/people/me")
    r.raise_for_status()
    data = r.json()

    return render_template("newVM.html",
                           name=" Bonjour, {}".format(data["displayName"]),
                           url=format(data["image"]["url"]))

@app.route("/creationVM")
def newVM():
    nom = request.form['nom']  # id="nom" pour l'input ciblé.
    coordX = request.form['coordX']  # id="coordX" pour l'input ciblé.
    coordY = request.form['coordY']  # etc ...

    conn = libvirt.open("qemu:///system")
    le_uuid = str(uuid.uuid4())
    le_nom = 'test2'
    xmlconfig = '<domain type="kvm"> <name>' + le_nom + '</name> <uuid>' + le_uuid + '</uuid> <metadata> <libosinfo:libosinfo xmlns:libosinfo="http://libosinfo.org/xmlns/libvirt/domain/1.0"> <libosinfo:os id="http://debian.org/debian/10"/> </libosinfo:libosinfo> </metadata> <memory>1048576</memory> <currentMemory>1048576</currentMemory> <vcpu>2</vcpu> <os> <type arch="x86_64" machine="q35">hvm</type> <boot dev="hd"/> </os> <features> <acpi/> <apic/> <vmport state="off"/> </features> <cpu mode="host-model"/> <clock offset="utc"> <timer name="rtc" tickpolicy="catchup"/> <timer name="pit" tickpolicy="delay"/> <timer name="hpet" present="no"/> </clock> <pm> <suspend-to-mem enabled="no"/> <suspend-to-disk enabled="no"/> </pm> <devices> <emulator>/usr/bin/qemu-system-x86_64</emulator> <disk type="file" device="disk"> <driver name="qemu" type="qcow2"/> <source file="/var/lib/libvirt/images/debian7server.qcow2"/> <target dev="vda" bus="virtio"/> </disk> <disk type="file" device="cdrom"> <driver name="qemu" type="raw"/> <source file="/home/admin/Téléchargements"/> <target dev="sda" bus="sata"/> <readonly/> </disk> <controller type="usb" model="qemu-xhci" ports="15"/> <interface type="network"> <source network="default"/> <mac address="52:54:00:ac:b4:d8"/> <model type="virtio"/> </interface> <console type="pty"/> <channel type="unix"> <source mode="bind"/> <target type="virtio" name="org.qemu.guest_agent.0"/> </channel> <channel type="spicevmc"> <target type="virtio" name="com.redhat.spice.0"/> </channel> <input type="tablet" bus="usb"/> <graphics type="spice" port="-1" tlsPort="-1" autoport="yes"> <image compression="off"/> </graphics> <sound model="ich9"/> <video> <model type="qxl"/> </video> <redirdev bus="usb" type="spicevmc"/> <redirdev bus="usb" type="spicevmc"/> <memballoon model="virtio"/> <rng model="virtio"> <backend model="random">/dev/urandom</backend> </rng> </devices> </domain>'
    print(xmlconfig)
    dom = conn.createXML(xmlconfig, 0)
    print(dom, dom.name())

    if not session.get("access_token"):
        return redirect("/logout")
    with requests.Session() as s:
        s.auth = OAuth2BearerToken(session["access_token"])
        r = s.get("https://www.googleapis.com/plus/v1/people/me")
    r.raise_for_status()
    data = r.json()
    return return render_template("newVM.html",name=" Bonjour, {}".format(data["displayName"]),url=format(data["image"]["url"]))

#Route pour afficher la page pour consulter toutes les VM
@app.route("/allVM")
def allVM():
    if not session.get("access_token"):
        return redirect("/logout")
    with requests.Session() as s:
        s.auth = OAuth2BearerToken(session["access_token"])
        r = s.get("https://www.googleapis.com/plus/v1/people/me")
    r.raise_for_status()
    data = r.json()

    listVM = []
    conn = libvirt.open("qemu:///system")
    mes_vms = conn.listDefinedDomains()
    domains = conn.listAllDomains(0)
    for domain in domains:
        dom = conn.lookupByName(domain.name())
        state, maxmem, mem, cpus, cput = dom.info()
        tab = { 
            "nom_machine":dom.name(),
        }
        listVM.append(tab)

    return render_template("allVM.html",
                           name=" Bonjour, {}".format(data["displayName"]),
                           url=format(data["image"]["url"]),
                           listVM=listVM)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True , host=host_projet)




"""
def add_admin():
    utilisateur = 'remplacer par la variable utlisateur selectionnï¿½'
    with open('new_users.txt') and open('customers.txt') as addadmin:
        if user in addadmin.read():
            file = open('admins.txt', "a")
            file.writelines(f'{user}\n')
            file.close()
            with open("new_users.txt", "r") as delete:
                lines = delete.readlines()
            with open("new_users.txt", "w") as delete:
                for line in lines:
                    if line.strip("\n") != utilisateur:
                        delete.write(line)


def add_customer():
    utilisateur = 'remplacer par la variable utlisateur selectionnï¿½'
    with open('new_users.txt') as addcustomer:
        if user in addcustomer.read():
            file = open('customers.txt', "a")
            file.writelines(f'{user}\n')
            file.close()
            with open("new_users.txt", "r") as delete:
                lines = delete.readlines()
            with open("new_users.txt", "w") as delete:
                for line in lines:
                    if line.strip("\n") != utilisateur:
                        delete.write(line)
    file.close()


def remove_permission():
    utilisateur = ''
    with open("new_users.txt", "r") and open("customers.txt", "r") and open("admins.txt", "r") as delete:
        lines = delete.readlines()
    with open("new_users.txt", "w") and ("customers", "w") and ("admins.txt", "w") as delete:
        for line in lines:
            if line.strip("\n") != utilisateur:
                delete.write(line)
    file.close()
"""
