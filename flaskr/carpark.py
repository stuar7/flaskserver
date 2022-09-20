import sqlite3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('carpark', __name__)

@bp.route('/')
def index():
    db = get_db()
    # posts = db.execute(
    #     'SELECT p.id, title, body, created, author_id, username'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' ORDER BY created DESC'
    # ).fetchall()
    # print(posts)
    carbays = db.execute(
        'SELECT c.id, pos1, pos2, width, height, colour'
        ' FROM carpark c'
        ' ORDER BY c.id'
    ).fetchall()
   # db.row_factory = sqlite3.Row
   # row = carbays.fetchone()

   # print(row)
   # for x in row:
   #     print(x) 
    return render_template('carpark/index.html', carbays=carbays)

def update_carbay(bay):
    updated_carbay = {}
    try:
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("UPDATE carpark SET pos1 = ?, pos2 = ?, height = ?, width = ?, colour = ? WHERE id = ?",  
                     (bay["pos1"], bay["pos2"], bay["height"], 
                     bay["width"], bay["colour"], 
                     bay["id"],))
        conn.commit()
        #return the user
        updated_carbay = get_carbay_by_id(bay["id"])
        print("carbay" + updated_carbay)
    except Exception as inst:
        print(inst)
        conn.rollback()
        updated_user = {}
    finally:
        conn.close()
    return updated_carbay


def get_carbay_by_id(bay_id):
    carbay = {}
    try:
        conn = db.get_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM carpark WHERE id = ?", 
                       (bay_id,))
        row = cur.fetchone()

        # convert row object to dictionary
        carbay["id"] = row["id"]
        carbay["pos1"] = row["pos1"]
        carbay["pos2"] = row["pos2"]
        carbay["width"] = row["width"]
        carbay["height"] = row["height"]
        carbay["colour"] = row["colour"]
    except:
        carbay = {}

    return carbay