import db

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
    return db.query("SELECT * FROM recipes WHERE user_id=?", [user_id])

def get_recipes():
    return db.query("SELECT * FROM recipes",)

def add_recipe_by_user(name, instructions, slug, username):
    user_id = db.query("SELECT id FROM users WHERE username = ?", [username])[0][0]
    sql = "INSERT INTO recipes (name, instructions, user_id, slug) VALUES (?, ?, ?, ?)"
    db.execute(sql, [name, instructions, user_id, slug])

def add_recipe(name, instructions, slug):
    db.execute("INSERT INTO recipes (name, instructions, slug) VALUES (?, ?, ?)", [name, instructions, slug])

def remove_recipe(recipe_id):
    db.execute("DELETE FROM recipes WHERE id = ?", [recipe_id])
    #Delete also from other tables where reference to recipe

def update_recipe(name, instructions, recipe_id, slug):
    sql = "UPDATE recipes SET name = ?, instructions = ?, slug = ? WHERE id = ?"
    db.execute(sql, [name, instructions, slug, recipe_id])

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
