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
    recipes = db.query("SELECT r.id, r.name, r.instructions, r.user_id, r.slug, r.image FROM recipes r WHERE id=?", [recipe_id])
    recipe = handle_images(recipes)
    return recipe if recipe else None

def get_recipe_by_slug(slug):
    recipes = db.query("SELECT r.id, r.name, r.instructions, r.user_id, r.slug, r.image FROM recipes r WHERE slug=?", [slug])
    recipe = handle_images(recipes)
    return recipe if recipe else None

def get_recipes_by_user(user_id):
    recipes = db.query("SELECT r.id, r.name, r.instructions, r.user_id, r.slug, r.image FROM recipes r WHERE user_id=?", [user_id])
    return handle_images(recipes)

def get_recipes():
    recipes = db.query("SELECT r.id, r.name, r.instructions, r.user_id, r.slug, r.image FROM recipes r",)
    return handle_images(recipes) if recipes else None

def handle_images(recipes):
    recipes_with_image = []
    for recipe in recipes:
        recipe_with_image = {}
        recipe_with_image["name"] = recipe["name"]
        recipe_with_image["instructions"] = recipe["instructions"]
        recipe_with_image["slug"] = recipe["slug"]
        recipe_with_image["id"] = recipe["id"]
        recipe_with_image["user_id"] = recipe["user_id"]
        if recipe["image"] and type(recipe["image"]) != str:
            recipe_with_image["image"] = base64.b64encode(recipe["image"]).decode("utf-8")
        elif recipe["image"]:
            recipe_with_image["image"] = recipe["image"]
        else: recipe_with_image["image"] = None
        recipes_with_image.append(recipe_with_image)
    return recipes_with_image

def add_recipe_by_user(name, tags, ingredients, instructions, slug, username, image):
    user_id = db.query("SELECT id FROM users WHERE username = ?", [username])[0][0]
    sql = "INSERT INTO recipes (name, instructions, user_id, slug, image) VALUES (?, ?, ?, ?, ?)"
    db.execute(sql, [name, instructions, user_id, slug, image])
    recipe_id = db.query("SELECT id FROM recipes WHERE name = ?", [name])[0][0]
    if ingredients:
        ingredients = clean_list(ingredients)
        for i in ingredients:
            if i:
                existing_id = db.query("SELECT id FROM ingredients WHERE name = ?", [i])
                if not existing_id:
                    sql = "INSERT INTO ingredients (name) VALUES (?)"
                    db.execute(sql, [i])
                    existing_id = db.query("SELECT id FROM ingredients WHERE name = ?", [i])[0][0]
                else:
                    existing_id = existing_id[0][0]
                sql_ingredient = "INSERT INTO recipe_ingredient (recipe_id, ingredient_id) VALUES (?, ?)"
                db.execute(sql_ingredient, [recipe_id, existing_id])
    if tags:
        for t in tags:
            tag_id = t[0]
            sql_tag = "INSERT INTO recipe_tag (recipe_id, tag_id) VALUES (?, ?)"
            db.execute(sql_tag, [recipe_id, tag_id])

def remove_recipe(recipe_id):
    db.execute("DELETE FROM recipe_ingredient WHERE recipe_id = ?", [recipe_id])
    db.execute("DELETE FROM recipe_tag WHERE recipe_id = ?", [recipe_id])
    db.execute("DELETE FROM recipes WHERE id = ?", [recipe_id])

def update_recipe(name, ingredients, instructions, recipe_id, slug, image, tags):
    sql = "UPDATE recipes SET name = ?, instructions = ?, slug = ?, image = ? WHERE id = ?"
    db.execute(sql, [name, instructions, slug, image, recipe_id])
    if ingredients:
        ingredients = clean_list(ingredients)
        for i in ingredients:
            existing_id = db.query("SELECT id FROM ingredients WHERE name = ?", [i])
            if not existing_id:
                sql = "INSERT INTO ingredients (name) VALUES (?)"
                db.execute(sql, [i])
                existing_id = db.query("SELECT id FROM ingredients WHERE name = ?", [i])[0][0]
            else:
                existing_id = existing_id[0][0]
            #check if already in recipe_ingredient table
            sql = "INSERT INTO recipe_ingredient (recipe_id, ingredient_id) VALUES (?, ?)"
            db.execute(sql, [recipe_id, existing_id])
    if tags:
        for t in tags:
            tag_id = t[0]
            existing_recipe_tag = db.query("SELECT tag_id FROM recipe_tag WHERE recipe_id = ? AND tag_id = ?", [recipe_id, tag_id])
            if not existing_recipe_tag:
                sql = "INSERT INTO recipe_tag (recipe_id, tag_id) VALUES (?, ?)"
                db.execute(sql, [recipe_id, tag_id])

def search(query):
    sql = "SELECT r.id, r.name, r.instructions, r.user_id, r.slug, r.image FROM recipes r WHERE instructions LIKE ? OR name LIKE ?"
    #Add ingredients to search
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

def get_slug(recipe_id):
    slug = db.query("SELECT slug FROM recipes WHERE id = ?", [recipe_id])[0][0]
    return slug if slug else None

def get_recipes_tags():
    return db.query("SELECT t.id, t.name, t.plural, t.slug FROM tags t",)

def get_recipes_by_tag(slug):
    sql = "SELECT r.id, r.name, r.instructions, r.user_id, r.slug, r.image FROM recipes r JOIN recipe_tag RT ON R.id = RT.recipe_id JOIN tags T ON rt.tag_id = t.id WHERE T.slug = ?"
    recipes = db.query(sql, [slug])
    return handle_images(recipes)

def get_tags_by_recipe(recipe_id):
    sql = "SELECT T.name FROM tags T JOIN recipe_tag RT ON T.id = RT.tag_id WHERE RT.recipe_id = ?"
    return db.query(sql, [recipe_id])

def get_tag_plural(slug):
    plural = db.query("SELECT plural FROM tags WHERE slug = ?", [slug])[0][0]
    return plural

def clean_list(list_to_clean):
    list_to_clean = list(dict.fromkeys(list_to_clean))
    for i in list_to_clean:
        if i is "":
           list_to_clean.remove(i)
    return list_to_clean

def get_ingredients(recipe_id):
    ingredients = db.query("SELECT I.name FROM ingredients I JOIN recipe_ingredient RI ON I.id = RI.ingredient_id WHERE RI.recipe_id = ?", [recipe_id])
    ingredient_names = []
    for i in ingredients:
        ingredient_names.append(i[0])
    return ingredient_names

def get_user_id(user):
    sql = "SELECT id FROM users WHERE username = ?"
    return db.query(sql, [user])

def get_username(user_id):
    sql = "SELECT username FROM users WHERE id = ?"
    username = db.query(sql, [user_id])
    return username[0][0] if username else None

def handle_tags(tags):
    tags = clean_list(tags)
    full_tags = []
    for t in tags:
        tag_name = t
        sql = "SELECT t.id, t.name, t.plural, t.slug FROM tags t WHERE name = ?"
        tag = db.query(sql, [tag_name])[0]
        full_tags.append(tag)
    return full_tags