import db

def recipe_name_free(name):
    sql = "SELECT name FROM recipes WHERE name=?"
    result = db.query(sql, [name])
    if result:
        return False
    else:
        return True

def get_recipe(slug):
    sql = "SELECT * FROM recipes WHERE slug=?"
    recipe = db.query(sql, [slug])
    return recipe

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
