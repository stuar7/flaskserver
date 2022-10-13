from datetime import datetime, timedelta, time
import sqlite3
from tracemalloc import start
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

    startDate = "2022-09-01"
    endDate = datetime.today().strftime('%Y-%m-%d')
   
    try:
        datemin = datetime.strptime(request.args.get('start-date'), '%Y-%m-%d').timestamp()
        startDate = request.args.get('start-date')
    except:
        datemin = None
    try:
        datemax = datetime.strptime(request.args.get('end-date'), '%Y-%m-%d').timestamp()
        endDate = request.args.get('end-date')
    except:
        datemax = None

    baystatus = 0
    try:
        baystatus = int(request.args.get('bay-status'))
    except:
        pass


    startTime = datetime.strptime("8:30", '%H:%M')
    endTime = datetime.strptime("17:30", '%H:%M')
    timeIsSet = False
    try:
        startTime = datetime.strptime(request.args.get('start-time'), '%H:%M:%S')
        endTime = datetime.strptime(request.args.get('end-time'), '%H:%M:%S')
        timeIsSet = True
    except Exception as inst:
        timeIsSet = False
        pass

    dateComparison = f""
    if(datemin):
        dateComparison += f" AND datetime(date, 'unixepoch', 'localtime') >= datetime({datemin}, 'unixepoch', 'localtime')"
        print(f"Date min: {datemin}")
    if(datemax):
        dateComparison += f" AND datetime(date, 'unixepoch', 'localtime') <= datetime({datemax}, 'unixepoch', 'localtime')"
        print(f"Date max: {datemax}")
    print(dateComparison)

    try:
        db = get_db()
        snapshot = db.execute(
            f'SELECT * FROM snapshot WHERE carparkname = \"{carparkname}\"{dateComparison};'
        ).fetchall()
        thiscarpark = db.execute(
            f'SELECT description FROM s_carpark WHERE carparkname = \"{carparkname}\"'
        ).fetchone()
        description = thiscarpark['description']
    
        snapshot = [dict(i) for i in snapshot]
        if(len(snapshot) == 0):
            return render_template('carpark/analysis.html',carparkname=carparkname, 
        dayBinEmpty=None, dayBinLabels=None,
        startDate=startDate, endDate=endDate, description=description,
        valuesCalculated=None,
        baystatus=baystatus, 
        startTime=datetime.strptime(f'{startTime.hour}:{startTime.minute}:00', '%H:%M:%S').strftime("%H:%M:%S"),
        endTime=datetime.strptime(f'{endTime.hour}:{endTime.minute}:00', '%H:%M:%S').strftime("%H:%M:%S"))
        
        
    except sqlite3.OperationalError as inst:
        print(inst)
        return Markup(f"<html><body><p>SQL Server Error!<br> {inst} </p></body></html>")
    
    numberOfBays = snapshot[0]['BAYS_EMPTY'] + snapshot[0]['BAYS_FULL'] +snapshot[0]['BAYS_UNKNOWN']
    print(numberOfBays)
    # Per Day
    currentDay = datetime.fromtimestamp(snapshot[0]['date']).day
    dayBinLabels = []
    dayBinEmpty = []
    # Full
    dayBinFull = 0
   
    # Unknown
    dayBinUnknown = 0
    # Empty
    dayBinEmpty = []
    statusBins = {'BAYS_EMPTY': [], 'BAYS_FULL': [], 'BAYS_UNKNOWN': []}

    dayBinIndex = 0
    currentDivisor = 1
    dayBinEmpty.append(snapshot[0]['BAYS_EMPTY'])
    dayBinLabels.append(f"{datetime.fromtimestamp(snapshot[0]['date']).strftime('%d%b')}")
    previousEntryDate = snapshot[0]['date']
    previousEntry = snapshot[0]
    print(statusBins)
    statusBins['BAYS_EMPTY'].append(previousEntry['BAYS_EMPTY'])
    statusBins['BAYS_FULL'].append(previousEntry['BAYS_FULL'])
    statusBins['BAYS_UNKNOWN'].append(previousEntry['BAYS_UNKNOWN'])
    print(statusBins)


    valuesCalculated = 0
    metric = ['BAYS_EMPTY', 'BAYS_FULL', 'BAYS_UNKNOWN']
    for index, entry in enumerate(snapshot):
        # Current Entry Time
        cET = datetime.fromtimestamp(entry['date'])
        # If the current info does not equal the current day.
        if(cET.day != currentDay):
            dayBinEmpty[dayBinIndex] /= currentDivisor
            statusBins['BAYS_EMPTY'][dayBinIndex] /= currentDivisor
            statusBins['BAYS_FULL'][dayBinIndex] /= currentDivisor
            statusBins['BAYS_UNKNOWN'][dayBinIndex] /= currentDivisor
            print(statusBins['BAYS_EMPTY'][dayBinIndex])
            print(dayBinEmpty[dayBinIndex])
            currentDay = datetime.fromtimestamp(entry['date']).day
            dayBinEmpty.append(entry[metric[baystatus]])
            statusBins['BAYS_EMPTY'].append(entry['BAYS_EMPTY'])
            statusBins['BAYS_FULL'].append(entry['BAYS_FULL'])
            statusBins['BAYS_UNKNOWN'].append(entry['BAYS_UNKNOWN'])
            currentDivisor = 0
            dayBinIndex +=1
            dayBinLabels.append(f"{cET.strftime('%d%b')}")
            valuesCalculated+=1
        else:
            if(timeIsSet):
                # Checks to see if time is between hour/minute range
                if(timeOfDayBetween(
                    time(startTime.hour, startTime.minute), 
                    time(endTime.hour, endTime.minute), 
                    time(cET.hour, cET.minute))):
                    # This entry falls inside our allowed time range
                    dayBinEmpty[dayBinIndex] += entry[metric[baystatus]]
                    statusBins['BAYS_EMPTY'][dayBinIndex] += entry['BAYS_EMPTY']
                    statusBins['BAYS_FULL'][dayBinIndex] += entry['BAYS_FULL']
                    statusBins['BAYS_UNKNOWN'][dayBinIndex] += entry['BAYS_UNKNOWN']
                    print(statusBins['BAYS_EMPTY'][dayBinIndex])
                    print(dayBinEmpty[dayBinIndex])
                    valuesCalculated+=1                    
                else:
                    currentDivisor -= 1
            else:
                # Previous Entry Time
                pTP = datetime.fromtimestamp(previousEntryDate)
                # Add 29 minutes to the previous entry time
                ptP_end = pTP + timedelta(minutes=29)
                # If this entry is within 29 minutes of the previous, we ignore it
                if(isCurrentInTimePeriod(
                    time(pTP.hour, pTP.minute), 
                    time(ptP_end.hour, ptP_end.minute), 
                    time(cET.hour, cET.minute))):
                    # This entry was too recent
                    currentDivisor -= 1
                else:
                    dayBinEmpty[dayBinIndex] += entry[metric[baystatus]]
                    statusBins['BAYS_EMPTY'][dayBinIndex] += entry['BAYS_EMPTY']
                    statusBins['BAYS_FULL'][dayBinIndex] += entry['BAYS_FULL']
                    statusBins['BAYS_UNKNOWN'][dayBinIndex] += entry['BAYS_UNKNOWN']
                    previousEntryDate = entry['date']
                    valuesCalculated+=1
        currentDivisor += 1
    if(currentDivisor > 1):
        statusBins['BAYS_EMPTY'][dayBinIndex] /= currentDivisor
        statusBins['BAYS_FULL'][dayBinIndex] /= currentDivisor
        statusBins['BAYS_UNKNOWN'][dayBinIndex] /= currentDivisor
    print(statusBins)
    #https://www.chartjs.org/docs/latest/samples/area/line-stacked.html
    return render_template('carpark/analysis.html',carparkname=carparkname, 
        dayBinEmpty=dayBinEmpty, dayBinLabels=dayBinLabels,
        startDate=startDate, endDate=endDate, description=description,
        valuesCalculated=valuesCalculated, 
        statusBins=statusBins,
        baystatus=baystatus, numberOfBays=numberOfBays,
        startTime=datetime.strptime(f'{startTime.hour}:{startTime.minute}:00', '%H:%M:%S').strftime("%H:%M:%S"),
        endTime=datetime.strptime(f'{endTime.hour}:{endTime.minute}:00', '%H:%M:%S').strftime("%H:%M:%S"))