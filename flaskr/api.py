from datetime import datetime
from flaskr.db import get_db

# TIME_DIFFERENCE dictates how long the last status update is valid for in seconds.
TIME_DIFFERENCE = 600

def create_carbay(json):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO ? (id,p1,p2,p3,p4,status,date) VALUES (?,?,?,?,?,?,?))",
                     (json["carpark"], json["id"], json["p1"], json["p2"], json["p3"], 
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
        cur.execute("UPDATE ? SET p1 = ?, p2 = ?, p3 = ?, p4 = ?, status = ?, date = ? WHERE id = ?",  
                     (json["carpark"], json["p1"], json["p2"], json["p3"], 
                     json["p4"], json["status"], datetime.now().timestamp(), 
                     json["id"])
                     )
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
        print(f"UPDATE { json['carpark']} SET status = \'{ json['status']}\', date = \'{ int(datetime.now().timestamp()) }\' WHERE id = { json['id']};")
        cur.execute(f"UPDATE { json['carpark']} SET status = \'{ json['status']}\', date = \'{ int(datetime.now().timestamp()) }\' WHERE id = { json['id']};")
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
        cur.execute("SELECT * FROM ? WHERE id = ?", 
                       (carpark, bay_id,))
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
            if int(datetime.now().timestamp()) - int(row[1]) > TIME_DIFFERENCE:
                non_responding+=1
            elif row[0] == 'empty':
                empty+=1
            elif row[0] == 'full':
                full+=1
    except Exception as inst:
        print(inst)
    return empty, full, non_responding