import db

def get_comments_by_recipe(recipe_id):
    comments = db.query("SELECT c.comment, c.id, u.username, c.sent_at FROM comments c LEFT JOIN users u ON u.id = c.user_id WHERE recipe_id = ?", [recipe_id])
    return comments if comments else []

def get_comments_by_user(user_id):
    comments = db.query("SELECT comment, id, recipe_id, sent_at FROM comments WHERE user_id = ?", [user_id])
    return comments if comments else []

def add_comment(user_id, recipe_id, comment):
    sql = "INSERT INTO comments (user_id, recipe_id, comment, sent_at) VALUES (?, ?, ?, datetime('now'))"
    db.execute(sql, [user_id, recipe_id, comment])