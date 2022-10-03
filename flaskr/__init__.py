import os
from socket import socket

from flask import Flask, request, jsonify #added to top of file
from flask_cors import CORS #added to top of file
from flask_socketio import SocketIO, send
from flask_mqtt import Mqtt

import sqlite3

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )



    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import carpark
    app.register_blueprint(carpark.bp)
    app.add_url_rule('/', endpoint='index')

    # API Route that updates all elements of a carbay entry
    @app.route('/api/update_entry',  methods = ['PUT'])
    def api_update_carbay_entry():
        carbay = request.get_json()
        print(carbay)
        return jsonify(carpark.update_carbay(carbay))
    
    # API Route that updates only the status of a carbay entry
    @app.route('/api/update_status',  methods = ['PUT'])
    def api_update_carbay_status():
        json = request.get_json()
        print(json)
        return jsonify(carpark.update_carbay_status(json))


    # mosquito settings
    app.config['SECRET_KEY'] = 'mysecret'
    app.config['MQTT_BROKER_URL'] = '127.0.0.1'
    app.config['MQTT_BROKER_PORT'] = 1883

    #
    mqtt = Mqtt(app)
    mqtt.subscribe('/carpark')
    socketio = SocketIO(app, cors_allowed_origins='*')

    #@socketio.on('message')
    #def handleMessage(msg):
    #    print('Message ' +msg)
    #    send(msg, boradcast=True)
    #    return jsonify(carpark.update_carbay_status(msg))
    @mqtt.on_connect()
    def handle_connect(client, userdata, flags, rc):
        if rc == 0:
            print('Connected successfully')
            mqtt.subscribe('/carpark') # subscribe topic
        else:
            print('Bad connection. Code:', rc)
            
    @mqtt.on_message()
    def handle_mqtt_message(client, userdata, message):
        #data = dict(
        ##topic=message.topic,
        #payload=message.payload.decode()
        #)
        #print('Received message on topic: {topic} with payload: {payload}'.format(**data))
        import json
        #print(message)
        print(message.payload.decode())
        msg = message.payload.decode().replace("'", '"')
        print(json.loads(msg))
        msg = json.loads(msg)
        if(message.topic == '/carpark'):
            with app.app_context():
                return jsonify(carpark.update_carbay_status(msg))
        else:
            return



    return app
