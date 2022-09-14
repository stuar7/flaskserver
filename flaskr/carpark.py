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
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
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
    return render_template('carpark/index.html', posts=posts, carbays=carbays)