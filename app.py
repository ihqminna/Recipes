from flask import Flask
from flask import render_template, request, redirect, session, abort
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import config
import db
import recipes

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    all_recipes = recipes.get_recipes()
    recipes_count = len(all_recipes)
    return render_template("index.html", count=recipes_count, recipes=all_recipes)

@app.route("/kirjaudu")
def login():
    return render_template("login.html")

@app.route("/kirjaasisaan", methods=["POST"])
def in_logger():
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
def register():
    return render_template("register.html")

@app.route("/uusikayttaja", methods=["POST"])
def new_user():
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
def own_recipes():
    username = session["user"]
    user_id = db.query("SELECT id FROM users WHERE username = ?", [username])[0][0]
    own_recipes = recipes.get_recipes_by_user(user_id)
    recipes_count = len(own_recipes)
    return render_template("own_recipes.html", count=recipes_count, recipes=own_recipes)

@app.route("/resepti/<slug>")
def show_recipe(slug):
    recipe = recipes.get_recipe_by_slug(slug)[0]
    if not recipe:
        abort(404)
    return render_template("show_recipe.html", recipe=recipe)

@app.route("/uusiresepti")
def new_recipe():
    return render_template("new_recipe.html")

@app.route("/kiitos")
def thank_you():
    return render_template("thank_you.html")

@app.route("/uusi", methods=["POST"])
def new():
    name = request.form["name"]
    instructions = request.form["instructions"]
    if len(name) > 0:
        if recipes.recipe_name_free(name):
            slug = recipes.create_slug(name)
            if session:
                username = session["user"]
                recipes.add_recipe_by_user(name, instructions, slug, username)
            else:
                recipes.add_recipe(name, instructions, slug)
            return redirect("/kiitos")
        else:
            return "Reseptin nimi on jo käytössä"
    else:
        return "Lisää reseptille nimi"

if __name__ == "__main__":
    app.run(debug=True)