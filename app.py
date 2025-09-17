from flask import Flask
from flask import render_template, request, redirect, session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    db.execute("INSERT INTO visits (visited_at) VALUES (datetime('now'))")
    recipes = db.query("SELECT name FROM recipes",)
    recipes_count = len(recipes)
    return render_template("index.html", count=recipes_count, recipes=recipes)

@app.route("/kirjaudu")
def kirjaudu():
    return render_template("kirjaudu.html")

@app.route("/kirjaasisaan", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    sql = "SELECT password_hash FROM users WHERE username = ?"
    password_hash = db.query(sql, [username])[0][0]

    if check_password_hash(password_hash, password):
        session["user"] = username
        return redirect("/omatreseptit")
    else:
        return "Väärä käyttäjätunnus tai salasana"

@app.route("/kirjaaulos")
def logout():
    del session["user"]
    return redirect ("/")

@app.route("/rekisteroidy")
def rekisteroidy():
    return render_template("rekisteroidy.html")

@app.route("/uusikayttaja", methods=["POST"])
def uusikayttaja():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "Salasanat eivät täsmää"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "Käyttäjätunnus on jo varattu, käytä toista käyttäjätunnusta"

    return "Käyttäjätunnus on luotu"

@app.route("/omatreseptit")
def recipes():
    return "<h1>Omat reseptisi</h1>"

@app.route("/reseptit1")
def resepti1():
    return "<h1>Resepti1</h1>"

@app.route("/uusiresepti")
def uusi_resepti():
    return render_template("uusi_resepti.html")

@app.route("/kiitos")
def kiitos():
    return render_template("kiitos.html")

@app.route("/uusi", methods=["POST"])
def uusi():
    name = request.form["name"]
    instructions = request.form["instructions"]
    db.execute("INSERT INTO recipes (name, instructions) VALUES (?, ?)", [name, instructions])
    return redirect("/kiitos")

if __name__ == "__main__":
    app.run(debug=True)
