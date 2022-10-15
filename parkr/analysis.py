from datetime import datetime, timedelta, time
import sqlite3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, Markup
)
from parkr.db import get_db


bp = Blueprint('analysis', __name__)

def isCurrentInTimePeriod(startTime, endTime, currentTime): 
    if startTime < endTime: 
        return currentTime >= startTime and currentTime <= endTime 
    else: 
        #Over midnight:
        return currentTime >= startTime or currentTime <= endTime

def timeOfDayBetween(s, e, c):
    if s < e:
        return c >= s and c <= e 
    else: 
        return False

@bp.route('/c/<string:carparkname>/analysis', methods=['GET', 'POST'])
def analysis(carparkname="carpark"):

    # Default start date on page load (today - 30 days)
    startDate = (datetime.today() - timedelta(days=30))
    endDate = datetime.today()

    # Default time
    startTime = datetime.strptime("8:30:00", '%H:%M:%S')
    endTime = datetime.strptime("17:30:00", '%H:%M:%S')
    # Try and parse GET time messages
    try:
        startTime = datetime.strptime(request.args.get('start-time'), '%H:%M:%S')
        endTime = datetime.strptime(request.args.get('end-time'), '%H:%M:%S')
    except Exception as inst:
        pass

    # Try and parse GET date messages
    try:
        datemin = datetime.strptime(f"{request.args.get('start-date')}-{startTime}", '%Y-%m-%d-%H:%M%S').timestamp()
        startDate = datetime.strptime(request.args.get('start-date'), '%Y-%m-%d')
    except:
        startDate = startDate + timedelta(hours=startTime.hour, minutes=startTime.minute)
        datemin = startDate.timestamp()
    try:
        datemax = datetime.strptime(f"{request.args.get('end-date')}-{endTime}", '%Y-%m-%d-%H:%M:%S').timestamp()
        endDate = datetime.strptime(request.args.get('end-date'), '%Y-%m-%d')
    except:
        endDate = endDate + timedelta(hours=endDate.hour, minutes=endDate.minute)
        datemax = endDate.timestamp()

    # Construct the date comparison for SQL lookup
    dateComparison = f""
    if(datemin):
        dateComparison += f" AND datetime(date, 'unixepoch', 'localtime') >= datetime({datemin}, 'unixepoch', 'localtime')"
        print(f"Date min: {datemin}")
    if(datemax):
        dateComparison += f" AND datetime(date, 'unixepoch', 'localtime') <= datetime({datemax}, 'unixepoch', 'localtime')"
        print(f"Date max: {datemax}")
    print(dateComparison)

    # Graph datapoint and label variables
    statusBins = {'BAYS_EMPTY': [], 'BAYS_FULL': [], 'BAYS_UNKNOWN': []}
    dayBinLabels = []
    # Fetch all our snapshot
    try:
        db = get_db()
        snapshot = db.execute(
            f'SELECT * FROM snapshot WHERE carparkname = \"{carparkname}\"{dateComparison};'
        ).fetchall()
        thiscarpark = db.execute(
            f'SELECT description FROM carparkregistry WHERE carparkname = \"{carparkname}\"'
        ).fetchone()
        description = thiscarpark['description']
    
        snapshot = [dict(i) for i in snapshot]
        # If the SQL fetch did not return anything, return empty page.
        if(len(snapshot) == 0):
            return render_template('carpark/analysis/analysis.html',carparkname=carparkname, 
        dayBinLabels=dayBinLabels,
        startDate=startDate.strftime('%Y-%m-%d'), endDate=endDate.strftime('%Y-%m-%d'), description=description,
        valuesCalculated=None, statusBins=statusBins,
        startTime=datetime.strptime(f'{startTime.hour}:{startTime.minute}:00', '%H:%M:%S').strftime("%H:%M:%S"),
        endTime=datetime.strptime(f'{endTime.hour}:{endTime.minute}:00', '%H:%M:%S').strftime("%H:%M:%S"))
        
    except sqlite3.OperationalError as inst:
        print(inst)
        return Markup(f"<html><body><p>SQL Server Error!<br> {inst} </p></body></html>")
    
    # Get number of bays for our Y axis.
    numberOfBays = snapshot[0]['BAYS_EMPTY'] + snapshot[0]['BAYS_FULL'] +snapshot[0]['BAYS_UNKNOWN']
    # Per Day
    currentDay = datetime.fromtimestamp(snapshot[0]['date']).date()
    dayBinIndex = 0
    currentDivisor = 1
    # Fill all the variables with the first entry to distinguish when the day has changed.
    dayBinLabels.append(f"{datetime.fromtimestamp(snapshot[0]['date']).strftime('%d%b')}")
    previousEntryDate = snapshot[0]['date']
    previousEntry = snapshot[0]
    statusBins['BAYS_EMPTY'].append(previousEntry['BAYS_EMPTY'])
    statusBins['BAYS_FULL'].append(previousEntry['BAYS_FULL'])
    statusBins['BAYS_UNKNOWN'].append(previousEntry['BAYS_UNKNOWN'])
    valuesCalculated = 0
    # For each entry in the database, we bin the data into the three categories for each day.
    for entry in snapshot:
        # Current Entry Time
        cET = datetime.fromtimestamp(entry['date'])
        # If the current entries date does not equal the day the current binning day.
        if(cET.date() != currentDay):
            # The day has changed so we finalize the previous day by finding the average.
            statusBins['BAYS_EMPTY'][dayBinIndex] /= currentDivisor
            statusBins['BAYS_FULL'][dayBinIndex] /= currentDivisor
            statusBins['BAYS_UNKNOWN'][dayBinIndex] /= currentDivisor
            # Move on to the next day
            currentDay = datetime.fromtimestamp(entry['date']).date()
            statusBins['BAYS_EMPTY'].append(entry['BAYS_EMPTY'])
            statusBins['BAYS_FULL'].append(entry['BAYS_FULL'])
            statusBins['BAYS_UNKNOWN'].append(entry['BAYS_UNKNOWN'])
            currentDivisor = 0
            dayBinIndex += 1
            dayBinLabels.append(f"{cET.strftime('%d%b')}")
            valuesCalculated += 1
            currentDivisor += 1
        else:
            # Previous Entry Time
            pTP = datetime.fromtimestamp(previousEntryDate)
            # Add 29 minutes to the previous entry time
            ptP_end = pTP + timedelta(minutes=29)
            # If this entry is within 29 minutes of the previous, we ignore it
            if(isCurrentInTimePeriod(time(pTP.hour, pTP.minute), time(ptP_end.hour, ptP_end.minute), 
                    time(cET.hour, cET.minute)) == False):
                # Checks to see if time is between hour/minute range
                if(timeOfDayBetween(time(startTime.hour, startTime.minute), 
                    time(endTime.hour, endTime.minute), 
                    time(cET.hour, cET.minute))):
                    # This entry falls inside our allowed time range
                    statusBins['BAYS_EMPTY'][dayBinIndex] += entry['BAYS_EMPTY']
                    statusBins['BAYS_FULL'][dayBinIndex] += entry['BAYS_FULL']
                    statusBins['BAYS_UNKNOWN'][dayBinIndex] += entry['BAYS_UNKNOWN']
                    previousEntryDate = entry['date']
                    valuesCalculated += 1
                    currentDivisor += 1
    # Finds the average bay value for the last index value
    if(currentDivisor > 1):
        statusBins['BAYS_EMPTY'][dayBinIndex] /= currentDivisor
        statusBins['BAYS_FULL'][dayBinIndex] /= currentDivisor
        statusBins['BAYS_UNKNOWN'][dayBinIndex] /= currentDivisor
    return render_template('carpark/analysis/analysis.html',carparkname=carparkname, 
        dayBinLabels=dayBinLabels,
        startDate=startDate.strftime('%Y-%m-%d'), endDate=endDate.strftime('%Y-%m-%d'), description=description,
        valuesCalculated=valuesCalculated, 
        statusBins=statusBins, numberOfBays=numberOfBays,
        startTime=datetime.strptime(f'{startTime.hour}:{startTime.minute}:00', '%H:%M:%S').strftime("%H:%M:%S"),
        endTime=datetime.strptime(f'{endTime.hour}:{endTime.minute}:00', '%H:%M:%S').strftime("%H:%M:%S"))
