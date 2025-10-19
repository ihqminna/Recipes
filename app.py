"""Main functionality of application."""
import sqlite3
import secrets
import time
from flask import Flask
from flask import render_template, request, redirect, session, abort, g
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import markupsafe
import config
import db
import math
import recipes
import comments

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    """Shows all recipes."""
    page_size = 24
    recipe_count = recipes.recipe_count()
    page_count = math.ceil(recipe_count/page_size)
    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))
    recipe_list = recipes.get_paged_recipes(page, page_size)
    return render_template("index.html", recipes=recipe_list, page=page, page_count=page_count)
    
@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    elapsed_time = round(time.time() - g.start_time, 2)
    print("elapsed time:", elapsed_time, "s")
    return response

@app.route("/kirjaudu")
def login():
    """Loads login page."""
    return render_template("login.html", filled=[], session=session, next_page=request.referrer)

@app.route("/kirjaasisaan", methods=["GET", "POST"])
def in_logger():
    """Logs user in or returns error message."""
    if request.method == "GET":
        return render_template("login.html", filled={}, session=session, next_page=request.referrer)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        next_page = request.form["next_page"]
        if next_page.endswith("/rekisteroidy"):
            next_page = "/"
        if not username or not password or len(username) > 20 or len(password) > 30:
            message =  "Väärä käyttäjätunnus tai salasana"
            filled = {"username": username}
            return render_template(
                "login.html",
                message=message,
                filled=filled,
                next_page=next_page
            )
        sql = "SELECT * FROM users WHERE username = ?"
        user_query = db.query(sql, [username])
        if not user_query:
            filled = {"username": username}
            message =  "Väärä käyttäjätunnus tai salasana"
            return render_template(
                "login.html",
                message=message,
                filled=filled,
                next_page=next_page
            )
        user = user_query[0]
        password_hash = user["password_hash"]
        if check_password_hash(password_hash, password):
            session["user"] = username
            session["user_id"] = user["id"]
            session["csrf_token"] = secrets.token_hex(16)
            return redirect(next_page)
        filled = {"username": username}
        message =  "Väärä käyttäjätunnus tai salasana"
    return render_template(
        "login.html",
        message=message,
        filled=filled,
        session=session,
        next_page=next_page
    )

@app.route("/kirjaaulos")
def logout():
    """Logs user out."""
    require_login()
    del session["user"]
    del session["user_id"]
    del session["csrf_token"]
    return redirect ("/")

@app.route("/rekisteroidy")
def register():
    """Loads registering page."""
    return render_template("register.html", filled=[], session=session)

@app.route("/uusikayttaja", methods=["GET", "POST"])
def new_user():
    """Adds new user or returns error message."""
    if request.method == "GET":
        return render_template("login.html", filled={})
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if not username or not password1 or not password2 or len(username) > 20:
            filled = {"username": username}
            message = "Tarkista täyttämäsi kentät."
            return render_template("register.html", message=message, filled=filled)
        if password1 != password2:
            filled = {"username": username}
            message = "Salasanat eivät täsmää"
            return render_template("register.html", message=message, filled=filled)
        password_hash = generate_password_hash(password1)
        try:
            sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
            db.execute(sql, [username, password_hash])
        except sqlite3.IntegrityError:
            message = "Käyttäjätunnus on varattu, käytä toista käyttäjätunnusta"
            return render_template("register.html", message=message)
        return redirect("/kirjaudu")
    return render_template("register.html", filled=[], session=session)

@app.route("/avainsanat")
def keywords():
    """Shows different tags."""
    tags = recipes.get_recipes_tags()
    return render_template("keywords.html", tags=tags)

@app.route("/avainsanat/<slug>")
def show_tag(slug, page=1):
    """Shows recipes with specific tag."""
    page_size = 24
    recipe_count = recipes.recipe_count_by_tag(slug)
    page_count = math.ceil(recipe_count/page_size)
    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))
    recipe_list = recipes.get_recipes_paged_by_tag(slug, page, page_size)
    plural = recipes.get_tag_plural(slug)
    return render_template("show_keyword.html", recipes=recipe_list, plural=plural, page=page, page_count=page_count)

@app.route("/<user>")
def show_user(user):
    """Shows user page."""
    require_login()
    user_id = recipes.get_user_id(user)
    if user_id and session:
        sessionuser = session["user"]
        user_id = user_id[0][0]
        comment_list = comments.get_comments_by_user(user_id)
        recipe_list = recipes.get_recipes_by_user(user_id)
        return render_template(
            "show_user.html",
            username=user,
            recipes=recipe_list,
            comments=comment_list,
            sessionuser=sessionuser
        )
    abort(404)

@app.route("/<user>/haku", methods=["GET"])
def search_user(user):
    """Searches from user's recipes."""
    require_login()
    user_id = recipes.get_user_id(user)
    if session and user_id:
        user_id = user_id[0][0]
        comment_list = comments.get_comments_by_user(user_id)
        sessionuser = session["user"]
        query = request.args.get("query")
        if query:
            results = recipes.search_by_user(query, user_id)
        else:
            results = []
        recipe_list = recipes.get_recipes_by_user(user_id)
        return render_template(
            "show_user.html",
            query=query,
            username=user,
            recipes=recipe_list,
            results=results,
            comments=comment_list,
            sessionuser=sessionuser
        )
    return render_template("/kirjaudu")

@app.route("/resepti/<slug>", methods=["GET", "POST"])
def show_recipe(slug):
    """Shows recipe page."""
    recipe = recipes.get_recipe_by_slug(slug)
    if not recipe:
        abort(404)
    else:
        recipe = recipe[0]
    recipe_id = recipe["id"]
    username = recipes.get_username(recipe["user_id"])
    ingredients = recipes.get_ingredients(recipe_id)
    tags = recipes.get_tags_by_recipe(recipe_id)
    message = ""
    if request.form.get("action") == "Lisää kommentti":
        csrf_token = request.form["csrf_token"]
        check_csrf(csrf_token)
        comment = request.form["comment"]
        if not comment:
            message = "Kirjoita nyt jotain!"
        else:
            user_id = session["user_id"]
            message = "Kiitos kommentistasi!"
            comments.add_comment(user_id, recipe_id, comment)
    comment_list = comments.get_comments_by_recipe(recipe_id)
    return render_template(
        "show_recipe.html",
        username=username,
        session=session,
        message=message,
        recipe=recipe,
        ingredients=ingredients,
        tags=tags,
        comments=comment_list
    )

@app.route("/uusiresepti")
def new_recipe():
    """Opens page for new recipe."""
    require_login()
    return render_template("new_recipe.html", session=session)

@app.route("/kiitos")
def thank_you():
    """Loads thank you page."""
    return render_template("thank_you.html")

@app.route("/uusi", methods=["POST", "GET"])
def new():
    """Adds new recipe or returns error message."""
    require_login()
    name = request.form["name"]
    name = str(name)
    csrf_token = request.form["csrf_token"]
    check_csrf(csrf_token)
    ingredients = request.form.getlist("ingredient")
    instructions = request.form["instructions"]
    tags = request.form.getlist("tag")
    tags = recipes.handle_tags(tags)
    all_tags = recipes.get_recipes_tags()
    imagefile = request.files["image"]
    text_check = recipe_text_checker(name, "", instructions)
    if text_check:
        message = text_check
        return render_template(
            "new_recipe.html",
            message=message,
            session=session,
            name=name,
            tags=tags,
            all_tags=all_tags,
            ingredients=ingredients,
            instructions=instructions,
            imagefile=imagefile
        )
    slug = recipes.create_slug(name)
    if request.form.get("action") == "Lisää ainesosa":
        ingredients = recipes.clean_list(ingredients)
        ingredients.append("")
        return render_template(
            "new_recipe.html",
            name=name,
            session=session,
            tags=tags,
            all_tags=all_tags,
            ingredients=ingredients,
            instructions=instructions,
            imagefile=imagefile
        )
    if request.form.get("action") == "Lisää avainsana":
        tags.append("")
        return render_template(
            "new_recipe.html",
            slug=slug,
            session=session,
            all_tags=all_tags,
            tags=tags, name=name,
            ingredients=ingredients,
            instructions=instructions,
            imagefile=imagefile
        )
    if imagefile:
        if imagefile.filename == "" or not imagefile.filename.endswith(".jpg"):
            message = "Tarkista kuvan tiedosto."
            return render_template(
                "new_recipe.html",
                message=message,
                session=session,
                name=name,
                tags=tags,
                all_tags=all_tags,
                ingredients=ingredients,
                instructions=instructions
            )
        image = imagefile.read()
        if len(image) > 1000000:
            message = "Liian suuri kuvatiedosto, maksimikoko 1Mt."
            return render_template(
                "new_recipe.html",
                message=message,
                session=session,
                name=name,
                tags=tags,
                all_tags=all_tags,
                ingredients=ingredients,
                instructions=instructions
            )
    else: image = None
    username = session["user"]
    recipe = {
        "name": name,
        "tags": tags,
        "ingredients": ingredients,
        "instructions": instructions,
        "slug": slug,
        "username": username,
        "image": image
    }
    recipes.add_recipe_by_user(recipe)
    return redirect("/kiitos")

@app.route("/poista/<slug>", methods=["GET", "POST"])
def remove_recipe(slug):
    """Removes a recipe."""
    require_login()
    recipe = recipes.get_recipe_by_slug(slug)
    if not recipe:
        abort(404)
    else:
        recipe = recipe[0]
    if recipe["user_id"] != session["user_id"]:
        abort(403)
    if request.method == "GET":
        return render_template("remove_recipe.html", recipe=recipe, session=session)
    if request.method == "POST":
        csrf_token = request.form["csrf_token"]
        check_csrf(csrf_token)
        if "remove" in request.form:
            recipes.remove_recipe(recipe["id"])
            return redirect("/")
        return redirect("/resepti/" + slug)
    return redirect("/resepti/" + slug)

@app.route("/muokkaa/<slug>")
def edit_recipe(slug):
    """Editing a recipe."""
    require_login()
    recipe = recipes.get_recipe_by_slug(slug)
    if not recipe:
        abort(404)
    else:
        recipe = recipe[0]
    if recipe["user_id"] != session["user_id"]:
        abort(403)
    recipe_id = recipe["id"]
    ingredients = recipes.get_ingredients(recipe_id)
    name = recipe["name"]
    instructions = recipe["instructions"]
    imagefile = recipe["image"]
    tags = recipes.get_tags_by_recipe(recipe_id)
    all_tags = recipes.get_recipes_tags()
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)
    return render_template(
        "edit_recipe.html",
        slug=slug,
        session=session,
        name=name,
        all_tags=all_tags,
        instructions=instructions,
        tags=tags,
        imagefile=imagefile,
        recipe_id=recipe_id,
        ingredients=ingredients
    )

@app.route("/haku", methods=["GET"])
def search():
    """Recipe search."""
    query = request.args.get("query")
    results = recipes.search(query) if query else []
    return render_template("index.html", query=query, results=results)

@app.route("/tallenna", methods=["POST"])
def save_recipe():
    """Saves an edited recipe or returns error."""
    require_login()
    csrf_token = request.form["csrf_token"]
    check_csrf(csrf_token)
    recipe_id = request.form["recipe_id"]
    old_recipe = recipes.get_recipe_by_id(recipe_id)
    old_recipe = old_recipe[0]
    slug = recipes.get_slug(recipe_id)
    all_tags = recipes.get_recipes_tags()
    if not old_recipe:
        abort(404)
    if old_recipe["user_id"] != session["user_id"]:
        abort(403)
    name = request.form["name"]
    old_name = old_recipe["name"]
    if not name:
        name = old_name
    name = str(name)
    ingredients = request.form.getlist("ingredient")
    instructions = request.form["instructions"]
    tags = request.form.getlist("tag")
    tags = recipes.handle_tags(tags)
    imagefile = request.files["image"]
    if not instructions:
        instructions = old_recipe["instructions"]
    text_check = recipe_text_checker(name, old_name, instructions)
    if text_check:
        message = text_check
        return render_template(
            "new_recipe.html",
            slug=slug,
            session=session,
            all_tags=all_tags,
            tags=tags,
            message=message,
            name=name,
            ingredients=ingredients,
            instructions=instructions,
            imagefile=imagefile
        )
    if request.form.get("action") == "Lisää ainesosa":
        ingredients = recipes.clean_list(ingredients)
        ingredients.append("")
        return render_template(
            "edit_recipe.html",
            slug=slug,
            session=session,
            all_tags=all_tags,
            tags=tags,
            recipe_id=recipe_id,
            name=name,
            ingredients=ingredients,
            instructions=instructions,
            imagefile=imagefile
        )
    if request.form.get("action") == "Lisää avainsana":
        tags.append("")
        return render_template(
            "edit_recipe.html",
            slug=slug,
            session=session,
            all_tags=all_tags,
            tags=tags,
            recipe_id=recipe_id,
            name=name,
            ingredients=ingredients,
            instructions=instructions,
            imagefile=imagefile
        )
    if imagefile:
        if imagefile.filename == "" or not imagefile.filename.endswith(".jpg"):
            message = "Tarkista kuvan tiedosto."
            return render_template(
                "edit_recipe.html",
                slug=slug,
                session=session,
                all_tags=all_tags,
                tags=tags,
                recipe_id=recipe_id,
                message=message,
                name=name,
                ingredients=ingredients,
                instructions=instructions
            )
        image = imagefile.read()
        if len(image) > 1000000:
            message = "Liian suuri kuvatiedosto, kuvan tulee olla alle 1Mt."
            return render_template(
                "edit_recipe.html",
                slug=slug,
                session=session,
                all_tags=all_tags,
                tags=tags,
                recipe_id=recipe_id,
                message=message,
                name=name,
                ingredients=ingredients,
                instructions=instructions
            )
    else:
        image = old_recipe["image"]
    slug = recipes.create_slug(name)
    recipe = {
        "name": name,
        "id": old_recipe["id"],
        "ingredients": ingredients,
        "instructions": instructions,
        "recipe_id": recipe_id,
        "slug": slug,
        "image": image,
        "tags": tags
    }
    recipes.update_recipe(recipe)
    return redirect("/resepti/" + slug)

def require_login():
    """Checks if user is logged in."""
    if "user_id" not in session:
        abort(403)

def check_csrf(csrf_token):
    """Checks csrf token."""
    if csrf_token != session["csrf_token"]:
        abort(403)

def recipe_text_checker(name, old_name, instructions):
    """Returns error message if name or instructions are not valid."""
    message = None
    if len(name) > 60 or len(instructions) > 300:
        message = "Tarkista tekstikenttien pituudet"
    if len(name) <= 0:
        message = "Lisää reseptille nimi."
    if name != old_name and not recipes.recipe_name_free(name):
        message = "Reseptin nimi on jo käytössä"
    return message if message else None

@app.template_filter()
def show_lines(content):
    """Shows content linebreaks."""
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

if __name__ == "__main__":
    app.run(debug=True)
