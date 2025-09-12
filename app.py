from flask import Flask
from flask import render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    db = sqlite3.connect("database.db")
    db.execute("INSERT INTO visits (visited_at) VALUES (datetime('now'))")
    db.commit()
    result = db.execute("SELECT COUNT(*) FROM visits").fetchone()
    count = result[0]
    db.close()
    return render_template("index.html", count=count)

@app.route("/reseptit")
def recipes():
    return "<h1>Reseptit</h1>"

@app.route("/reseptit/resepti1")
def resepti1():
    return "<h1>Resepti1</h1>"

@app.route("/uusiresepti")
def uusi_resepti():
    return render_template("uusi_resepti.html")

if __name__ == "__main__":
    app.run(debug=True)
