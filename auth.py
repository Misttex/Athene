import logging
import os

import pika
from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import re
import libvirt

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(20)
hote = '192.168.1.82'


#RabbitMQ création des queues
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='creation')
channel.queue_declare(queue='suppression')
channel.queue_declare(queue='travail_finis')
channel.queue_declare(queue='modification')
channel.queue_declare(queue='rename')
channel.queue_declare(queue='publication')

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
            flash("Ce compte existe déjà.", "danger")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Adresse Email invalide.", "danger")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Le nom d'utilisateur ne doit contenir que des caractères et des chiffres !", "danger")
        elif not username or not password or not email:
            flash("Vos identifiant sont invalides !", "danger")
        else:
            db.execute("INSERT INTO accounts(username,email,password) VALUES (:username, :email, :password)",
                       {"username": username, "email": email, "password": password})
            db.commit()
            flash("Tu as été enregistrer avec succes !", "success")
            return redirect(url_for('login'))

    elif request.method == 'POST':
        flash("Veuillez remplir le formulaire !", "danger")
    return render_template('auth/register.html', title="Register")


@app.route('/athene/home')
def home():
    if 'loggedin' in session:
        def size_format(size_in_bytes, unit):
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
                state = 'Bloqu�'
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
            listVMPerso.append(tab)
        return render_template('home/home.html', listVMPerso=listVMPerso, username=session['username'], title="Home")
    return redirect(url_for('login'))


@app.route("/athene/start_stop_machine", methods=['GET', 'POST'])
def start_stop_machine():
    if 'loggedin' in session:
        channel.basic_publish(exchange='', routing_key='OnOff',body='')
        print("Action OnOff")
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
        channel.basic_publish(exchange='', routing_key='suppression', body='Hello World!')
        print("Action 'Suppression'")
    return redirect(url_for('login'))


@app.route("/athene/creationVmFunction", methods=['GET', 'POST'])
def creationVmFunction():
    import subprocess
    import uuid
    if 'loggedin' in session:
        channel.basic_publish(exchange='', routing_key='creation', body='Hello World!')
        print(" [x] Sent 'Hello World!'")
    return redirect(url_for('login'))


@app.route('/athene/profile')
def profile():
    if 'loggedin' in session:
        return render_template('auth/profile.html', username=session['username'], title="Profile")
    return redirect(url_for('login'))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True, host=hote, port="1500")