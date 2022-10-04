1. Go to the directory with setup.py
2. Run [might be pip3]: pip install -e .
3. Run [to start the server]: flask --app flaskr --debug run

If no database is present: 
    Run: flask --app flaskr init-db
A carpark table will need to be manually created.


MQTT - Message Queuing Telemetry Transport:
Windows: https://delightnet.nl/index.php/mqtt/12-mqtt-broker-installation
For accessability purposes, this smart-parking demo uses "allow_anonymous true" for mosquitto.conf.
Linux:
Mac:

Base Flask and SQLite server:
https://flask.palletsprojects.com/en/2.2.x/tutorial/database/