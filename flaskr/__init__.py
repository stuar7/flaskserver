import os

from flask import Flask, request, jsonify #added to top of file
from flask_cors import CORS #added to top of file

from .db import get_db
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

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

  #  @app.route('/api/carbay', methods=['GET'])
  #  def api_get_users():
  #      return jsonify(get_carbay())

    @app.route('/api/carbay/update',  methods = ['PUT'])
    def api_update_carbay():
        carbay = request.get_json()
        print(carbay)
        return jsonify(update_carbay(carbay))

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import carpark
    app.register_blueprint(carpark.bp)
    app.add_url_rule('/', endpoint='index')

    return app

def update_carbay(bay):
    updated_carbay = {}
    try:
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("UPDATE carpark SET pos1 = ?, pos2 = ?, height = ?, width = ?, colour = ? WHERE id = ?",  
                     (bay["pos1"], bay["pos2"], bay["height"], 
                     bay["width"], bay["colour"], 
                     bay["id"],))
        conn.commit()
        #return the user
        updated_carbay = get_carbay_by_id(bay["id"])
        print("carbay" + updated_carbay)
    except Exception as inst:
        print(inst)
        print(inst.args)
        print((type(inst)))
        print("are we getting an exception")
        conn.rollback()
        updated_user = {}
    finally:
        conn.close()
    print("Did we get here")
    return updated_carbay


def get_carbay_by_id(bay_id):
    carbay = {}
    try:
        conn = db.get_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM carpark WHERE id = ?", 
                       (bay_id,))
        row = cur.fetchone()

        # convert row object to dictionary
        carbay["id"] = row["id"]
        carbay["pos1"] = row["pos1"]
        carbay["pos2"] = row["pos2"]
        carbay["width"] = row["width"]
        carbay["height"] = row["height"]
        carbay["colour"] = row["colour"]
    except:
        carbay = {}

    return carbay