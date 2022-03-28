import os
import logging
import requests
from requests_oauth2.services import GoogleClient
from requests_oauth2 import OAuth2BearerToken
from flask import Flask, request, redirect, session, render_template
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import logout_user
import libvirt_connec

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(20)
blueprint = make_google_blueprint()
app.register_blueprint(blueprint, url_prefix="/accueil/")

google_auth = GoogleClient(
    client_id=("554229061086-np1qvffgq6gi1f6njg99qkeqt4h2gaut"
               ".apps.googleusercontent.com"),
    client_secret="XqTsoS6DXq-W0KgTqvQISBOM",
    redirect_uri="http://localhost:5000/google/oauth2callback",
)


@app.route("/")
def index():
    return redirect("/logout")


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

    listVMPerso = [["Ubuntu", "linux", "Machine fictif"],
              ["Debian", "Linux", "Machine fictif"],
              ["Windows S", "Windows", "Machine fictif"]]
    # print(data)
    """emails = data["emails"]
    for d in emails:
        emails = d["value"]
    with open('new_users.txt') and open('admins.txt') and open('customers.txt') as txt:
        if not emails in txt.read():
            file = open("new_users.txt", "a")
            file.writelines(f'{emails}\n')
            file.close()"""
    return render_template("index.html", name="Bonjour, {}".format(data["displayName"]),
                           url=format(data["image"]["url"]),listVMPerso=listVMPerso)

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

#Route pour afficher la page de création VM
@app.route("/newVM")
def newVM():
    if not session.get("access_token"):
        return redirect("/logout")
    with requests.Session() as s:
        s.auth = OAuth2BearerToken(session["access_token"])
        r = s.get("https://www.googleapis.com/plus/v1/people/me")
    r.raise_for_status()
    data = r.json()
    # print(data)
    """emails = data["emails"]
    for d in emails:
        emails = d["value"]
    with open('new_users.txt') and open('admins.txt') and open('customers.txt') as txt:
        if not emails in txt.read():
            file = open("new_users.txt", "a")
            file.writelines(f'{emails}\n')
            file.close()"""

    return render_template("newVM.html",name="Bonjour, {}".format(data["displayName"]),
                           url=format(data["image"]["url"]))

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

    listVM = [["Ubuntu","linux","Machine fictif"],
              ["Debian","Linux","Machine fictif"],
              ["Windows S","Windows","Machine fictif"],
              ["Rocky Linux","Linux","Machine fictif"]]

    # print(data)
    """emails = data["emails"]
    for d in emails:
        emails = d["value"]
    with open('new_users.txt') and open('admins.txt') and open('customers.txt') as txt:
        if not emails in txt.read():
            file = open("new_users.txt", "a")
            file.writelines(f'{emails}\n')
            file.close()"""

    return render_template("allVM.html",name="Bonjour, {}".format(data["displayName"]),
                           url=format(data["image"]["url"]),listVM=listVM)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)




"""
def add_admin():
    utilisateur = 'remplacer par la variable utlisateur selectionné'
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
    utilisateur = 'remplacer par la variable utlisateur selectionné'
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
