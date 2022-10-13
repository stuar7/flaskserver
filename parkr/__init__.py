from datetime import datetime, timedelta
import time
import os
import threading
from flask import Flask, current_app, request, jsonify
from flask_mqtt import Mqtt
from parkr.dbfunctions import log_carpark_and_display, update_carbay, update_carbay_status, get_carpark_stats
import json

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # DB Directory
    dbdir = os.path.join(app.instance_path, 'parkr.sqlite')
    # Flask App Config
    app.config.from_mapping(
        SECRET_KEY='dev', #unused
        DATABASE=dbdir,
    )
    app.config.from_mapping(test_config)
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)    

    from . import homepage
    app.register_blueprint(homepage.bp)
    #app.add_url_rule('/', endpoint='index') #???

    from . import carpark
    app.register_blueprint(carpark.bp)

    from . import analysis
    app.register_blueprint(analysis.bp)

    # MQTT Settings
    app.config['SECRET_KEY'] = 'mysecret' #unused
    app.config['MQTT_BROKER_URL'] = '127.0.0.1'
    app.config['MQTT_BROKER_PORT'] = 1883

    # MQTT Initialize
    mqtt = Mqtt(app)
    mqtt.subscribe('/carpark')
    #socketio = SocketIO(app, cors_allowed_origins='*')

    @mqtt.on_connect()
    def handle_connect(client, userdata, flags, rc):
        if rc == 0:
            print('Connected successfully')
            mqtt.subscribe('/carpark')
        else:
            print('Bad connection. Code:', rc)
            
    # MQTT Message Listener
    @mqtt.on_message()
    def handle_mqtt_message(client, userdata, message):
        try:
            print(message.payload.decode())
            msg = json.loads(message.payload.decode())
            if(message.topic == '/carpark'):
                if "logging" in msg and msg['logging'] == True:
                    with app.app_context():
                        return jsonify(log_carpark_and_display(msg))
                else:
                    with app.app_context():
                        return jsonify(update_carbay_status(msg))
        except Exception as inst:
            print(inst)
            return

    # Snapshot function
    # This takes a snapshot of the current database every 30 minutes for each carpark
    def snapshot():
        print(f"Snapshot loaded in thread: {threading.current_thread()}")
        while True:
            minute_seconds = datetime.now().minute*60
            seconds = datetime.now().second
            time_seconds = minute_seconds + seconds
            sleeptime = 60*60 - time_seconds if time_seconds > 30*60 else 30*60 - time_seconds
            print(f"{int(sleeptime/60)}m{int((sleeptime)/60%1*60)}s until next snapshot.")
            time.sleep(sleeptime)
            timestamp = datetime.now().timestamp()
            try:
                with app.app_context():
                    conn = db.get_db()
                    carparks = conn.execute(
                        'SELECT carparkname FROM s_carpark'
                    ).fetchall()
                    for current_carpark in carparks:
                        e, f, n = get_carpark_stats(current_carpark[0])
                        conn.execute(f"INSERT INTO snapshot (carparkname, BAYS_EMPTY, BAYS_FULL, BAYS_UNKNOWN, date) VALUES (\'{current_carpark[0]}\',{e}, \'{f}\', \'{n}\', {timestamp});")
                        print(f"INSERT INTO snapshot (carparkname, BAYS_EMPTY, BAYS_FULL, BAYS_UNKNOWN, date) VALUES (\'{current_carpark[0]}\',{e}, \'{f}\', \'{n}\', {timestamp});")
                        conn.commit()
            except Exception as inst:
                print(f"Error with SQL server: {inst}")

    # Starts a new thread or the snapshot function
    def startSnapshot():  
        global snapshotThread
        snapshotThread = threading.Thread(target=snapshot)
        snapshotThread.daemon=True
        snapshotThread.start()
    startSnapshot()

 

    return app
