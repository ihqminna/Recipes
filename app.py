from flask import Flask
from flask import render_template, request, redirect
import db

app = Flask(__name__)

@app.route("/")
def index():
    db.execute("INSERT INTO visits (visited_at) VALUES (datetime('now'))")
    recipes = db.query("SELECT name FROM recipes",)
    recipes_count = len(recipes)
    return render_template("index.html", count=recipes_count, recipes=recipes)

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
