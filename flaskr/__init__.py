import os

from flask import Flask, request, jsonify #added to top of file
from flask_cors import CORS #added to top of file

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

    return app
