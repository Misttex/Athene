from flask import Flask,render_template, redirect, url_for
import jinja2


app=Flask(__name__)

@app.route('/')
def home():
    list = ['test', 'toto']
    return render_template('index.html', name = "Hello tout le monde",list = list)

@app.route('/<name>')
def user(utilisateur):
    return render_template('index.html',name = f"Hello {utilisateur}")

@app.route('/admin')
def admin():
    return render_template('index.html',name = f"Hello admin")

if __name__=="__main__":
    app.run(debug=True, use_reloader=False)