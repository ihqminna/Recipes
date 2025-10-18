import db

def get_comments_by_recipe(recipe_id):
    comments = db.query("SELECT comment, id, user_id FROM comments WHERE recipe_id = ?", [recipe_id])
    return comments if comments else []

def get_comments_by_user(user_id):
    comments = db.query("SELECT comment, id, recipe_id FROM comments WHERE user_id = ?", [user_id])
    return comments if comments else []