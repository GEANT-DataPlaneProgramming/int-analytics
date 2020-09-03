import pandas as pd
from influxdb import InfluxDBClient

host = 'localhost'
port = 8086
"""Instantiate a connection to the InfluxDB."""
user = 'root'
password = 'root'
dbname = 'int_telemetry'
dbuser = 'int'
dbuser_password = 'my_secret_password'

data = pd.read_csv("./int_data.txt", sep=" ",
                   names=["source_ip", "destination_ip", "source_port", "destination_port", "protocol",
                          "origin_timestamp", "destination_timestamp", "sequence_number"], header=None)

client = InfluxDBClient(host, port, user, password, dbname)

print("Create database: " + dbname)
client.create_database(dbname)


#print("Create a retention policy")
#client.create_retention_policy('flow_monitoring_policy', 'INF', 3, default=True)

print("Switch user: " + dbuser)
client.switch_user(dbuser, dbuser_password)

for index, row in data.iterrows():

    FLOW1 = {
        "srcip": row['source_ip'],
        "dstip": row['destination_ip'],
        "scrp": row['source_port'],
        "dstp": row['destination_port']
    }

    json_body = [{
        "measurement": "int_telemetry",
        "tags": FLOW1,
        'time': row['destination_timestamp'],
        "fields": {
            "origts": row['origin_timestamp'],
            "dstts": row['destination_timestamp'],
            "seq": row['sequence_number'],
        }
    }]

    print("Write points: {0}".format(json_body))
    client.write_points(json_body)
