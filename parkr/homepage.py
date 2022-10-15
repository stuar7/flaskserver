from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from parkr.db import get_db
import parkr.dbfunctions as fetch

bp = Blueprint('homepage', __name__)

# TIME_DIFFERENCE dictates how long the last status update is valid for in seconds.
TIME_DIFFERENCE = 5000

@bp.route('/')
def index():
    db = get_db()
    carparks = db.execute(
        'SELECT carparkname, points, description, x, y'
        ' FROM carparkregistry c'
    ).fetchall()
    carparks = [dict(i) for i in carparks]
    for count, currlist in enumerate(carparks):
        empty, full, non_responding = fetch.get_carpark_stats(currlist['carparkname'])
        currlist['empty'] = empty
        currlist['full'] = full
        currlist['non_responding'] = non_responding
    return render_template('index.html', carparks=carparks)

@bp.route('/redirect')
def redirect():
    return "Null"       