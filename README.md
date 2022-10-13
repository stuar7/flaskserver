# Smart Parking
## Installation
1. Change directory to the root directory.
2. (Optional) Create your own virtual environment.
3. Run: pip install -r requirements.txt
4. Set up MQTT (Message Queuing Telemetry Transport) service:

    Windows: https://delightnet.nl/index.php/mqtt/12-mqtt-broker-installation

    For accessability purposes, this smart-parking demo uses "allow_anonymous true" for mosquitto.conf.

    Linux: https://www.vultr.com/docs/install-mosquitto-mqtt-broker-on-ubuntu-20-04-server/

    Mac: https://formulae.brew.sh/formula/mosquitto
5. A database is present, but may be initialized with:
    flask --app parkr init-db
A table for each carpark will need to be manually created, along with the sensor entries.

## App Layout:
| File/Directory  | Description |
| ------------- | ------------- |
| \_\_init\_\_.py  | The main Flask application file. Each module is initialized here. |
| homepage.py  | Contains code relating to the index page |
| carpark.py  | Contains code relating to the car park pages. Each car park is dynamically created. |
| analysis.py | Contains code relating to the data analysis for each car park. |
| db.py  | Contains code relating to SQLite database initialization and loading |
| dbfunctions.py  | Contains functions that interact with the SQLite databse |
    

## Components based on:
Base Flask and SQLite server:
https://flask.palletsprojects.com/en/2.2.x/tutorial/

Stacked Line Graph:
https://www.chartjs.org/docs/latest/samples/area/line-stacked.html


# Issues & Compatability Problems
Requires Python3

Complete termination of the app requires discarding the terminal the program was launched in, otherwise threads may continue to exist.

# Run The Server
flask --app parkr run --host=0.0.0.0 --no-reload --with-threads

--host=0.0.0.0 will make the website available on all network interfaces. It is advisable to select a specific ip address.
