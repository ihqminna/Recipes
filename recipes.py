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
    recipes = db.query("SELECT * FROM recipes WHERE id=?", [recipe_id])
    recipe = handle_images(recipes)
    return recipe if recipe else None

def get_recipe_by_slug(slug):
    recipes = db.query("SELECT * FROM recipes WHERE slug=?", [slug])
    recipe = handle_images(recipes)
    return recipe if recipe else None

def get_recipes_by_user(user_id):
    recipes = db.query("SELECT * FROM recipes WHERE user_id=?", [user_id])
    return handle_images(recipes)

def get_recipes():
    recipes = db.query("SELECT * FROM recipes",)
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

def add_recipe_by_user(name, ingredients, instructions, slug, username, image):
    user_id = db.query("SELECT id FROM users WHERE username = ?", [username])[0][0]
    sql = "INSERT INTO recipes (name, instructions, user_id, slug, image) VALUES (?, ?, ?, ?, ?)"
    db.execute(sql, [name, instructions, user_id, slug, image])
    if ingredients:
        ingredients = ingredients_clean(ingredients)
        recipe_id = db.query("SELECT id FROM recipes WHERE name = ?", [name])[0][0]
        for i in ingredients:
            if i:
                existing_id = db.query("SELECT id FROM ingredients WHERE name = ?", [i])
                if not existing_id:
                    sql = "INSERT INTO ingredients (name) VALUES (?)"
                    db.execute(sql, [i])
                    existing_id = db.query("SELECT id FROM ingredients WHERE name = ?", [i])[0][0]
                else:
                    existing_id = existing_id[0][0]
                sql = "INSERT INTO recipe_ingredient (recipe_id, ingredient_id) VALUES (?, ?)"
                db.execute(sql, [recipe_id, existing_id])

def add_recipe(name, ingredients, instructions, slug, image):
    db.execute("INSERT INTO recipes (name, instructions, slug, image) VALUES (?, ?, ?, ?)", [name, instructions, slug, image])
    if ingredients:
        ingredients = ingredients_clean(ingredients)
        recipe_id = db.query("SELECT id FROM recipes WHERE name = ?", [name])[0][0]
        for i in ingredients:
            if i:
                existing_id = db.query("SELECT id FROM ingredients WHERE name = ?", [i])
                if not existing_id:
                    sql = "INSERT INTO ingredients (name) VALUES (?)"
                    db.execute(sql, [i])
                    existing_id = db.query("SELECT id FROM ingredients WHERE name = ?", [i])[0][0]
                else:
                    existing_id = existing_id[0][0]
                sql = "INSERT INTO recipe_ingredient (recipe_id, ingredient_id) VALUES (?, ?)"
                db.execute(sql, [recipe_id, existing_id])

def remove_recipe(recipe_id):
    db.execute("DELETE FROM recipes WHERE id = ?", [recipe_id])
    #Delete also from other tables where references to recipe (recipe_ingredient, recipe_tag)

def update_recipe(name, ingredients, instructions, recipe_id, slug, image):
    sql = "UPDATE recipes SET name = ?, instructions = ?, slug = ?, image = ? WHERE id = ?"
    db.execute(sql, [name, instructions, slug, image, recipe_id])
    if ingredients:
        ingredients = ingredients_clean(ingredients)
        for i in ingredients:
            if i:
                existing_id = db.query("SELECT id FROM ingredients WHERE name = ?", [i])
                if not existing_id:
                    sql = "INSERT INTO ingredients (name) VALUES (?)"
                    db.execute(sql, [i])
                    existing_id = db.query("SELECT id FROM ingredients WHERE name = ?", [i])[0][0]
                else:
                    existing_id = existing_id[0][0]
                sql = "INSERT INTO recipe_ingredient (recipe_id, ingredient_id) VALUES (?, ?)"
                db.execute(sql, [recipe_id, existing_id])

def search(query):
    sql = "SELECT * FROM recipes WHERE instructions LIKE ? OR name LIKE ?"
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

def get_tags():
    return db.query("SELECT * FROM tags",)

def get_recipes_by_tag(slug):
    sql = "SELECT R.* FROM recipes R JOIN recipe_tag RT ON R.id = RT.recipe_id JOIN tags T ON rt.tag_id = t.id WHERE T.slug = ?"
    recipes = db.query(sql, [slug])
    return handle_images(recipes)

def get_tags_by_recipe(recipe_id):
    sql = "SELECT T.name FROM tags T JOIN recipe_tag RT ON T.id = RT.tag_id WHERE RT.recipe_id = ?"
    return db.query(sql, [recipe_id])

def get_tag_plural(slug):
    plural = db.query("SELECT plural FROM tags WHERE slug = ?", [slug])[0][0]
    return plural

def ingredients_clean(ingredients):
    ingredients = list(dict.fromkeys(ingredients))
    for i in ingredients:
        if i is "":
            ingredients.remove(i)
    return ingredients

def get_ingredients(recipe_id):
    ingredients = db.query("SELECT I.name FROM ingredients I JOIN recipe_ingredient RI ON I.id = RI.ingredient_id WHERE RI.recipe_id = ?", [recipe_id])
    ingredient_names = []
    for i in ingredients:
        ingredient_names.append(i[0])
    return ingredient_names