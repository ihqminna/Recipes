from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Tervetuloa sovellukseen!"

@app.route("/reseptit")
def recipes():
    return "Reseptit"

@app.route("/reseptit/resepti1")
def resepti1():
    return "Resepti1"
