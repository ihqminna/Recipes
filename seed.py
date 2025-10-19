import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM recipe_tag")
db.execute("DELETE FROM recipe_ingredient")
db.execute("DELETE FROM ingredients")
db.execute("DELETE FROM comments")
db.execute("DELETE FROM recipes")
db.execute("DELETE FROM users")

user_count = 1000
recipe_count = 1000000

for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username) VALUES (?)", ["user" + str(i)])

for i in range(1, recipe_count + 1):
    db.execute("INSERT INTO recipes (name) VALUES (?)", ["recipe" + str(i)])
    tag_id = random.randint(1, 10)
    recipe_id = i
    sql_tags = """
    INSERT INTO recipe_tag (recipe_id, tag_id)
    VALUES (?, ?)
    """
    db.execute(sql_tags, [recipe_id, tag_id])

db.commit()
db.close()
