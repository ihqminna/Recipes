import sqlite3
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

    sql = "SELECT * FROM users WHERE username = ?"
    user_query = db.query(sql, [username])
    if not user_query:
        message =  "Väärä käyttäjätunnus tai salasana"
        return render_template("login.html", message=message) 
    else:
        user = user_query[0] 

    password_hash = user["password_hash"]

    if check_password_hash(password_hash, password):
        session["user"] = username
        session["user_id"] = user["id"]
        return redirect("/omatreseptit")
    else:
        message =  "Väärä käyttäjätunnus tai salasana"
        return render_template("login.html", message=message)
    
@app.route("/kirjaaulos")
def logout():
    del session["user"]
    del session["user_id"]
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
        message = "Salasanat eivät täsmää"
        return render_template("register.html", message=message)
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        message = "Käyttäjätunnus on varattu, käytä toista käyttäjätunnusta"
        return render_template("register.html", message=message)

    return redirect("/kirjaudu")

@app.route("/omatreseptit")
def own_recipes():
    if session:
        username = session["user"]
        user_id = db.query("SELECT id FROM users WHERE username = ?", [username])[0][0]
        own_recipes = recipes.get_recipes_by_user(user_id)
        recipes_count = len(own_recipes)
        return render_template("own_recipes.html", count=recipes_count, recipes=own_recipes)
    else:
        return render_template("/kirjaudu")

@app.route("/avainsanat")
def keywords():
    tags = recipes.get_tags()
    return render_template("keywords.html", tags=tags)

@app.route("/avainsanat/<slug>")
def show_tag(slug):
    recipe_list = recipes.get_recipes_by_tag(slug)
    plural = recipes.get_tag_plural(slug)
    return render_template("show_keyword.html", recipes=recipe_list, plural=plural)

@app.route("/resepti/<slug>")
def show_recipe(slug):
    recipe = recipes.get_recipe_by_slug(slug)[0]
    if not recipe:
        abort(404)
    print(recipe)
    recipe_id = recipe["id"]
    ingredients = recipes.get_ingredients(recipe_id)
    tags = recipes.get_tags_by_recipe(recipe_id)
    return render_template("show_recipe.html", recipe=recipe, ingredients=ingredients, tags=tags)

@app.route("/uusiresepti")
def new_recipe():
    return render_template("new_recipe.html")

@app.route("/kiitos")
def thank_you():
    return render_template("thank_you.html")

@app.route("/uusi", methods=["POST", "GET"])
def new():
    name = request.form["name"]
    name = str(name)
    ingredients = request.form.getlist("ingredient")
    instructions = request.form["instructions"]
    imagefile = request.files["image"]

    if request.form.get("action") == "Lisää ainesosa":
        ingredients = recipes.ingredients_clean(ingredients)
        ingredients.append("")
        return render_template("new_recipe.html", name=name, ingredients=ingredients, instructions=instructions, imagefile=imagefile)
    
    if not len(name) > 0:
        message = "Lisää reseptille nimi"
        return render_template("new_recipe.html", message=message, name=name, ingredients=ingredients, instructions=instructions, imagefile=imagefile)
    if not recipes.recipe_name_free(name):
        message = "Reseptin nimi on jo käytössä"
        return render_template("new_recipe.html", message=message, name=name, ingredients=ingredients, instructions=instructions, imagefile=imagefile)
    slug = recipes.create_slug(name)
    if imagefile:
        if imagefile.filename == "":
            message = "Lisää kuvatiedostolle nimi."
            return render_template("new_recipe.html", message=message, name=name, ingredients=ingredients, instructions=instructions)
        elif not imagefile.filename.endswith(".jpg"):
            message = "Kuvalla on väärä tiedostomuoto, lisää kuva jpg-muodossa."
            return render_template("new_recipe.html", message=message, name=name, ingredients=ingredients, instructions=instructions)
        image = imagefile.read()
        if len(image) > 1024*1024:
            message = "Liian suuri kuvatiedosto."
            return render_template("new_recipe.html", message=message, name=name, ingredients=ingredients, instructions=instructions)            
    else: image = None
    if session:
        username = session["user"]
        recipes.add_recipe_by_user(name, ingredients, instructions, slug, username, image)
    else:
        recipes.add_recipe(name, ingredients, instructions, slug, image)
    return redirect("/kiitos")
    
@app.route("/poista/<slug>", methods=["GET", "POST"])
def remove_recipe(slug):
    recipe = recipes.get_recipe_by_slug(slug)[0]
    if recipe["user_id"] != session["user_id"]:
        abort(403)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)
    
    if request.method == "GET":
        return render_template("remove_recipe.html", recipe=recipe)

    if request.method == "POST":
        if "remove" in request.form:
            recipes.remove_recipe(recipe["id"])
            return redirect("/")
        else:
            return redirect("/resepti/" + slug)
        
@app.route("/muokkaa/<slug>")
def edit_recipe(slug):
    recipe = recipes.get_recipe_by_slug(slug)[0]
    if recipe["user_id"] != session["user_id"]:
        abort(403)
    recipe_id = recipe["id"]
    ingredients = recipes.get_ingredients(recipe_id)
    name = recipe["name"]
    instructions = recipe["instructions"]
    imagefile = recipe["image"]
    tags = recipes.get_tags_by_recipe(recipe_id)
    all_tags = recipes.get_tags()
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)
    return render_template("edit_recipe.html", name=name, all_tags=all_tags, instructions=instructions, tags=tags, imagefile=imagefile, recipe_id=recipe_id, ingredients=ingredients)

@app.route("/omatreseptit/haku", methods=["GET"])
def search_own():
    if session:
        query = request.args.get("query")
        results = recipes.search(query) if query else []
        return render_template("own_recipes.html", query=query, results=results)
    else:
        return render_template("/kirjaudu")

@app.route("/haku", methods=["GET"])
def search():
    query = request.args.get("query")
    results = recipes.search(query) if query else []
    return render_template("index.html", query=query, results=results)

@app.route("/tallenna", methods=["POST"])
def save_recipe():
    recipe_id = request.form["recipe_id"]
    old_recipe = recipes.get_recipe_by_id(recipe_id)[0]
    slug = recipes.get_slug(recipe_id)
    if not old_recipe:
        abort(404)
    if old_recipe["user_id"] != session["user_id"]:
        abort(403)
    name = request.form["name"]
    name = str(name)
    old_name = old_recipe["name"]
    if not name:
        name = old_name
    ingredients = request.form.getlist("ingredient")
    instructions = request.form["instructions"]
    if not instructions:
        instructions = old_recipe["instructions"]
    imagefile = request.files["image"]
    if request.form.get("action") == "Lisää ainesosa":
        ingredients = recipes.ingredients_clean(ingredients)
        ingredients.append("")
        return render_template("edit_recipe.html", slug=slug, recipe_id=recipe_id, name=name, ingredients=ingredients, instructions=instructions, imagefile=imagefile)
    if imagefile:
        if imagefile.filename == "":
            message = "Lisää kuvatiedostolle nimi."
            return render_template("edit_recipe.html", slug=slug, recipe_id=recipe_id, message=message, name=name, ingredients=ingredients, instructions=instructions)
        elif not imagefile.filename.endswith(".jpg"):
            message = "Kuvalla on väärä tiedostomuoto, lisää kuva jpg-muodossa."
            return render_template("edit_recipe.html", slug=slug, recipe_id=recipe_id, message=message, name=name, ingredients=ingredients, instructions=instructions)
        image = imagefile.read()
        if len(image) > 1024*1024:
            message = "Liian suuri kuvatiedosto."
            return render_template("edit_recipe.html", slug=slug, recipe_id=recipe_id, message=message, name=name, ingredients=ingredients, instructions=instructions)            
    else: image = old_recipe["image"]
    if len(name) > 0:
        if name != old_name and not recipes.recipe_name_free(name):
            return "Reseptin nimi on jo käytössä"
            return render_template("edit_recipe.html", recipe_id=recipe_id, message=message, name=name, ingredients=ingredients, instructions=instructions, imagefile=imagefile)
        else:    
            slug = recipes.create_slug(name)
            recipes.update_recipe(name, ingredients, instructions, recipe_id, slug, image)
            return redirect("/resepti/" + slug)
    else:
        message = "Lisää reseptille nimi"
        return render_template("edit_recipe.html", slug=slug, recipe_id=recipe_id, message=message, name=name, ingredients=ingredients, instructions=instructions, imagefile=imagefile) 

if __name__ == "__main__":
    app.run(debug=True)