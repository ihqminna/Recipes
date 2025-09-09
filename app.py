from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/reseptit")
def recipes():
    return "<h1>Reseptit</h1>"

@app.route("/reseptit/resepti1")
def resepti1():
    return "<h1>Resepti1</h1>"

if __name__ == "__main__":
    app.run(debug=True)
