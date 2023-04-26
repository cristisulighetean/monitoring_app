import os
import time
import requests
import schedule
from flask import Flask
from influxdb import InfluxDBClient
from psycopg2 import connect
from psycopg2.extras import DictCursor

app = Flask(__name__)

# Database configurations
db_config = {
    "user": os.environ["DATABASE_USER"],
    "password": os.environ["DATABASE_PASSWORD"],
    "host": os.environ["DATABASE_HOST"],
    "port": os.environ["DATABASE_PORT"],
    "dbname": os.environ["DATABASE_NAME"]
}

# InfluxDB configurations
influxdb_config = {
    "host": os.environ["INFLUXDB_HOST"],
    "port": os.environ["INFLUXDB_PORT"],
    "username": os.environ["INFLUXDB_USERNAME"],
    "password": os.environ["INFLUXDB_PASSWORD"],
    "database": os.environ["INFLUXDB_DATABASE"]
}

# Connect to InfluxDB
influxdb_client = InfluxDBClient(**influxdb_config)
influxdb_client.switch_database(influxdb_config["database"])

def get_sensors():
    with connect(**db_config, cursor_factory=DictCursor) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM sensor")
            sensors = cursor.fetchall()
    return sensors

def query_sensor_data(sensor):
    url = f"http://{sensor['ip']}/data"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Extract the timestamp and measurements from the JSON data
        timestamp = data.get("timestamp", None)
        temp = data["temp"]["data"]
        pressure = data["pressure"]["data"]
        eco2 = data["eco2"]["data"]
        tvoc = data["tvoc"]["data"]

        # Package the data in InfluxDB line protocol format
        influx_data = [
            {
                "measurement": sensor["name"],
                "tags": {
                    "sensor_id": sensor["id"],
                    "sensor_name": sensor["name"],
                },
                "time": timestamp,
                "fields": {
                    "temperature": float(temp),
                    "pressure": float(pressure),
                    "eco2": int(eco2),
                    "tvoc": int(tvoc),
                },
            }
        ]

        # Write data to InfluxDB
        influxdb_client.write_points(influx_data)

def query_sensors():
    sensors = get_sensors()

    if not sensors:  # No sensors in the database
        print("No sensors found. Skipping query.")
        return

    for sensor in sensors:
        query_sensor_data(sensor)

# Schedule the query_sensors function to run every minute
schedule.every(1).minutes.do(query_sensors)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(5)
