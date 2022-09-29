from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('carpark', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/redirect')
def redirect():
    print("Redirected")
    return

@bp.route('/<string:carparkname>/')
@bp.route('/<string:carparkname>')
def carpark(carparkname="carpark"):
    db = get_db()
    carbays = db.execute(
        'SELECT c.id, p1, p2, p3, p4, status, date'
        f' FROM {carparkname} c'
        ' ORDER BY c.id'
    ).fetchall()
    TIME_DIFFERENCE = 500
    colour = []
    for x in carbays:
        time_difference = int(datetime.now().timestamp()) - int(x['date'])
        if(time_difference > TIME_DIFFERENCE):
            colour.append("gray")
        elif(time_difference < TIME_DIFFERENCE):
            if(x['status'] == "full"):
                colour.append("red")
            elif(x['status'] == "empty"):
                colour.append("green")
            elif([x['status'] == "gray"]):
                colour.append("gray")
    carbays = [dict(i) for i in carbays]
    for count, currlist in enumerate(carbays):
        currlist['colour'] = colour[count]

    carparkimage = db.execute(
        'SELECT carparkname, imageurl'
        ' FROM s_carpark c'
        f' WHERE carparkname="{carparkname}"'
    ).fetchall()
    imageurl = carparkimage[0][1]
    return render_template('carpark/index.html', carbays=carbays, carparkimage=imageurl, carparkname=carparkname)

def update_carbay(json):
    updated_carbay = {}
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE ? SET p1 = ?, p2 = ?, p3 = ?, p4 = ?, status = ?, date = ? WHERE id = ?",  
                     (json["carpark"], json["p1"], json["p2"], json["p3"], 
                     json["p4"], json["status"], datetime.now().timestamp(), 
                     json["id"])
                     )
        conn.commit()
        #return the user
        updated_carbay = get_carbay_by_id(json["id"])
        print("carbay" + str(updated_carbay))
    except Exception as inst:
        print(inst)
        conn.rollback()
    finally:
        conn.close()
    return updated_carbay

def update_carbay_status(json):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE ? status = ?, date = ? WHERE id = ?",
                    (json["carpark"], json["status"], datetime.now(),
                    json["id"])
                    )
        conn.commit()
    except Exception as inst:
        print(inst)
        conn.rollback()
    finally:
        conn.close()
    return

def get_carbay_by_id(bay_id):
    carbay = {}
    try:
        conn = get_db()
       # conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM carpark WHERE id = ?", 
                       (bay_id,))
        row = cur.fetchone()

        # convert row object to dictionary
        carbay["id"] = row["id"]
        carbay["p1"] = row["p1"]
        carbay["p2"] = row["p2"]
        carbay["p3"] = row["p3"]
        carbay["p4"] = row["p4"]
        carbay["colour"] = row["colour"]
        carbay["date"] = row["date"]
    except:
        carbay = {}
    return carbay