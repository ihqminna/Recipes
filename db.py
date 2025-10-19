"""Database connector."""
import sqlite3
from flask import g

def get_connection():
    """Opens database connection."""
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=[]):
    """Executes database inserts."""
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()

def last_insert_id():
    """Returns last database insert."""
    return g.last_insert_id

def query(sql, params=[]):
    """Return database query."""
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result
