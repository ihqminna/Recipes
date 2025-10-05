import db
import base64
from collections import namedtuple

def recipe_name_free(name):
    sql = "SELECT name FROM recipes WHERE name=?"
    result = db.query(sql, [name])
    if result:
        return False
    else:
        return True

def get_recipe_by_id(recipe_id):
    sql = "SELECT * FROM recipes WHERE id=?"
    return db.query(sql, [recipe_id])

def get_recipe_by_slug(slug):
    sql = "SELECT * FROM recipes WHERE slug=?"
    return db.query(sql, [slug])

def get_recipes_by_user(user_id):
    recipes = db.query("SELECT * FROM recipes WHERE user_id=?", [user_id])
    return handle_images(recipes)

def get_recipes():
    recipes = db.query("SELECT * FROM recipes",)
    return handle_images(recipes)

def handle_images(recipes):
    recipes_with_image = []
    for recipe in recipes:
        recipe_with_image = {}
        recipe_with_image["name"] = recipe["name"]
        recipe_with_image["instructions"] = recipe["instructions"]
        recipe_with_image["slug"] = recipe["slug"]
        if recipe["image"]:
            recipe_with_image["image"] = base64.b64encode(recipe["image"]).decode("utf-8")
        else: recipe_with_image["image"] = None
        recipes_with_image.append(recipe_with_image)
    return recipes_with_image

def add_recipe_by_user(name, instructions, slug, username, image):
    user_id = db.query("SELECT id FROM users WHERE username = ?", [username])[0][0]
    sql = "INSERT INTO recipes (name, instructions, user_id, slug, image) VALUES (?, ?, ?, ?, ?)"
    db.execute(sql, [name, instructions, user_id, slug, image])

def add_recipe(name, instructions, slug, image):
    db.execute("INSERT INTO recipes (name, instructions, slug, image) VALUES (?, ?, ?, ?)", [name, instructions, slug, image])

def remove_recipe(recipe_id):
    db.execute("DELETE FROM recipes WHERE id = ?", [recipe_id])
    #Delete also from other tables where reference to recipe

def update_recipe(name, instructions, recipe_id, slug, image):
    sql = "UPDATE recipes SET name = ?, instructions = ?, slug = ?, image = ? WHERE id = ?"
    db.execute(sql, [name, instructions, slug, image, recipe_id])

def search(query):
    sql = "SELECT * FROM recipes WHERE instructions LIKE ? OR name LIKE ?"
    #Add more possibilities to search
    return db.query(sql, ["%" + query + "%", "%" + query + "%"])

def create_slug(name):
    slug = ""
    for i in name:
        if i == "ä":
            add = "a"
        elif i == "ö":
            add = "o"
        elif i.isalpha():
            add = i
        elif i == " ":
            add = "_"
        else:
            add = ""
        slug = slug + add
    return slug

def get_tags():
    return db.query("SELECT * FROM tags",)

def get_recipes_by_tag(slug):
    sql = "SELECT R.* FROM recipes R JOIN recipe_tag RT ON R.id = RT.recipe_id JOIN tags T ON rt.tag_id = t.id WHERE T.slug = ?"
    recipes = db.query(sql, [slug])
    return recipes

def get_tag_plural(slug):
    plural = db.query("SELECT plural FROM tags WHERE slug = ?", [slug])[0][0]
    return plural