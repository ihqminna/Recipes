from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Tervetuloa sovellukseen!</h1>"

@app.route("/reseptit")
def recipes():
    return "<h1>Reseptit</h1>"

@app.route("/reseptit/resepti1")
def resepti1():
    return "<h1>Resepti1</h1>"

if __name__ == "__main__":
    app.run(debug=True)
