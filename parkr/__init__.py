import os
from socket import socket
from flask import Flask, request, jsonify
from flask_cors import CORS 
from flask_socketio import SocketIO, send
from flask_mqtt import Mqtt
from parkr.dbfunctions import update_carbay, update_carbay_status
import json

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', #unused
        DATABASE=os.path.join(app.instance_path, 'parkr.sqlite'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
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
    app.add_url_rule('/', endpoint='index')

    from . import carpark
    app.register_blueprint(carpark.bp)

    # API Route that updates all elements of a carbay entry
    @app.route('/api/update_entry',  methods = ['PUT'])
    def api_update_carbay_entry():
        carbay = request.get_json()
        print(carbay)
        return jsonify(update_carbay(carbay))
    
    # API Route that updates only the status of a carbay entry
    @app.route('/api/update_status',  methods = ['PUT'])
    def api_update_carbay_status():
        json = request.get_json()
        print(json)
        return jsonify(update_carbay_status(json))

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
        msg = message.payload.decode().replace("'", '"')
        try:
            msg = json.loads(msg)
            #print(json.loads(msg))
            if(message.topic == '/carpark'):
                with app.app_context():
                    return jsonify(update_carbay_status(msg))
        except Exception as inst:
            print(inst)
            return

    return app
