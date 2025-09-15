from flask import Flask
from flask import render_template, request
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    db = sqlite3.connect("database.db")
    db.execute("INSERT INTO visits (visited_at) VALUES (datetime('now'))")
    db.commit()
    recipes = db.execute("SELECT name, instructions FROM recipes").fetchall()
    db.close()
    count = len(recipes)
    return render_template("index.html", recipes_no=count, recipes=recipes)

@app.route("/omatreseptit")
def recipes():
    return "<h1>Omat reseptisi</h1>"

@app.route("/reseptit1")
def resepti1():
    return "<h1>Resepti1</h1>"

@app.route("/uusiresepti")
def uusi_resepti():
    return render_template("uusi_resepti.html")

@app.route("/kiitos", methods=["POST"])
def kiitos():
    name = request.form["name"]
    instructions = request.form["instructions"]
    db = sqlite3.connect("database.db")
    db.execute("INSERT INTO recipes (name, instructions) VALUES (?, ?)", [name, instructions])
    db.commit()
    db.close()
    return render_template("kiitos.html")

if __name__ == "__main__":
    app.run(debug=True)
