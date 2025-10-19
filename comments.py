"""Functions needed for handling comments."""
import db

def get_comments_by_recipe(recipe_id):
    """Returns comments of a recipe."""
    sql = """
    SELECT c.comment, c.id, u.username, c.sent_at 
    FROM comments c 
    LEFT JOIN users u ON u.id = c.user_id 
    WHERE recipe_id = ?
    """
    comments = db.query(sql, [recipe_id])
    return comments if comments else []

def get_comments_by_user(user_id):
    """Returns comments of a user."""
    sql = """
    SELECT comment, id, recipe_id, sent_at 
    FROM comments 
    WHERE user_id = ?
    """
    comments = db.query(sql, [user_id])
    return comments if comments else []

def add_comment(user_id, recipe_id, comment):
    """Adds comment to database."""
    sql = """
    INSERT INTO comments (user_id, recipe_id, comment, sent_at) 
    VALUES (?, ?, ?, datetime('now'))
    """
    db.execute(sql, [user_id, recipe_id, comment])
