from datetime import datetime
from parkr.db import get_db

# TIME_DIFFERENCE dictates how long the last status update is valid for in seconds.
TIME_DIFFERENCE = 600

def create_carbay(json):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(f"INSERT INTO {json['carpark']} (id,p1,p2,p3,p4,status,date) VALUES (?,?,?,?,?,?,?))",
                     (json["id"], json["p1"], json["p2"], json["p3"], 
                     json["p4"], json["status"], datetime.now().timestamp(),)
                     )
        conn.commit()
    except Exception as inst:
        print(inst)
        conn.rollback()
    finally:
        conn.close()
    return

def update_carbay(json):
    updated_carbay = {}
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(f"UPDATE {json['carpark']} SET p1 = \'{json['p1']}\', p2 = \'{json['p2']}\', p3 = \'{json['p3']}\', p4 = \'{json['p4']}\', status = \'{json['status']}\', date = \'{datetime.now().timestamp()}\' WHERE id = {json['id']};")
        conn.commit()
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
        print(f"UPDATE { json['carpark']} SET status = \'{ json['status']}\', date = \'{ datetime.now().timestamp() }\' WHERE id = { json['id']};")
        cur.execute(f"UPDATE { json['carpark']} SET status = \'{ json['status']}\', date = \'{ datetime.now().timestamp() }\' WHERE id = { json['id']};")
        conn.commit()
    except Exception as inst:
        print(inst)
        conn.rollback()
    finally:
        conn.close()
    return

def get_carbay_by_id(carpark, bay_id):
    carbay = {}
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {carpark} WHERE id = {bay_id};")
        row = cur.fetchone()
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

def get_carpark_stats(carpark):
    empty = 0
    full = 0
    non_responding = 0
    try:
        db = get_db()
        statusinfo = db.execute(f"SELECT status, date FROM {carpark}"
        ).fetchall()
        for row in statusinfo:
            if int(datetime.now().timestamp()) - int(float(row[1])) > TIME_DIFFERENCE:
                non_responding+=1
            elif row[0][0:5] == 'empty':
                empty+=1
            elif row[0] == 'full':
                full+=1
    except Exception as inst:
        print(inst)
    return empty, full, non_responding

def log_carpark_and_display(json):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(f"INSERT INTO sensorlog (carparkname, id, status, date) VALUES (\'{json['carpark']}\',{json['id']}, \'{json['status']}\', \'{datetime.now().timestamp()}\');")
        conn.commit()
        cur.execute(f"UPDATE { json['carpark']} SET status = \'{ json['status']}\', date = \'{ datetime.now().timestamp() }\' WHERE id = { json['id']};")
        conn.commit()
    except Exception as inst:
        print(inst)
        conn.rollback()
    finally:
        conn.close()
    return