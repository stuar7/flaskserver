from datetime import datetime
from PIL import Image
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from parkr.db import get_db
import parkr.dbfunctions as fetch

bp = Blueprint('carpark', __name__)

# TIME_DIFFERENCE dictates how long the last status update is valid for in seconds.
# 600 = 10 minutes
TIME_DIFFERENCE = 600

@bp.route('/c/<string:carparkname>/')
@bp.route('/c/<string:carparkname>')
def carpark(carparkname="carpark"):
    db = get_db()
    carbays = db.execute(
        f'SELECT id, p1, p2, p3, p4, status, date FROM {carparkname} ORDER BY id'
    ).fetchall()

    # For loop below determines which colour to mark the carbay as
    colour = []
    for x in carbays:
        time_difference = float(datetime.now().timestamp()) - int(float(x['date']))
        if(time_difference > TIME_DIFFERENCE):
            colour.append("gray")
        elif(time_difference < TIME_DIFFERENCE):
            if(x['status'] == "full"):
                colour.append("red")
            elif(x['status'] == "empty"):
                colour.append("lightgreen")
            elif(x['status'] == "gray"):
                colour.append("gray")
            elif(x['status'] == "empty_disabled"):
                colour.append("lightblue")
            elif(x['status'] == "empty_staff"):
                colour.append("orange")
    carbays = [dict(i) for i in carbays]
    for count, currlist in enumerate(carbays):
        currlist['colour'] = colour[count]
        # Find the center of the 4 point polygon to position the text displaying parking bay id
        currlist['centerx'] = (int(currlist['p1'].split(',')[0]) + int(currlist['p2'].split(',')[0]) + int(currlist['p3'].split(',')[0]) +int(currlist['p4'].split(',')[0]))/4 + (-5 if currlist['id'] < 10 else -8 if currlist['id'] < 100 else -11)
        currlist['centery'] = (int(currlist['p1'].split(',')[1]) + int(currlist['p2'].split(',')[1]) + int(currlist['p3'].split(',')[1]) +int(currlist['p4'].split(',')[1]))/4 + 5

    # A seperate table, carparkregistry, holds unique information regarding the carpark (name, image used)
    carparktable = db.execute(
        'SELECT carparkname, imageurl, description'
        ' FROM carparkregistry c'
        f' WHERE carparkname="{carparkname}"'
    ).fetchall()
    imageurl = carparktable[0][1]
    description = carparktable[0][2]

    # Dimensions for the background image for the SVG elements to map on to
    dimensions = [0,0]
    im = Image.open(f'./parkr/static/images/carpark/{imageurl}')
    dimensions[0], dimensions[1] = im.size

    # Car park statistics
    empty, full, non_responding = fetch.get_carpark_stats(carparkname)

    # Current Time
    currentTime = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    return render_template('carpark/carpark.html', 
        carbays=carbays, carparkimage=imageurl, 
        carparkname=carparkname, description=description, 
        dimensions=dimensions, empty=empty,
        full=full, non_responding=non_responding, currentTime=currentTime
    )
        