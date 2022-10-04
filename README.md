## Smart Parking
# Installation
1. Change directory to the root directory with setup.py
2. Run: pip install -e .
3. Set up MQTT (Message Queuing Telemetry Transport) service:
    Windows: https://delightnet.nl/index.php/mqtt/12-mqtt-broker-installation
    For accessability purposes, this smart-parking demo uses "allow_anonymous true" for mosquitto.conf.
    Linux:
    Mac:
4. A database is present, but may be initialized with:
    flask --app parkr init-db
A table for each carpark will need to be manually created, along with the sensor entries.

# App Layout:
__init__.py
homepage.py
carpark.py
db.py
api.py
    

# Components based on:
    Base Flask and SQLite server:
    https://flask.palletsprojects.com/en/2.2.x/tutorial/database/

# Run The Server
<<<<<<< HEAD:README.txt
flask --app parkr run --host=0.0.0.0
=======
flask --app flaskr run --host=0.0.0.0
>>>>>>> 3d67df2eb36affa8f8ee9f07fb212322b66fc971:README.md
