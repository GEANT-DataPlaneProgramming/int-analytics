from influxdb import InfluxDBClient
import time
import random

host = 'localhost'
port = 8086
"""Instantiate a connection to the InfluxDB."""
user = 'root'
password = 'root'
dbname = 'int_telemetry'
dbuser = 'int'
dbuser_password = 'my_secret_password'

client = InfluxDBClient(host, port, user, password, dbname)

print("Create database: " + dbname)
client.create_database(dbname)

print("Switch user: " + dbuser)
client.switch_user(dbuser, dbuser_password)

MILION = 1000000
for i in range(1000):
    timestamp = int(time.time() * 1e9)
    print('Timestamp is {0}'.format(timestamp))

    json_body =[{'fields': {
                            'origts': timestamp, 
                            'dstts': timestamp+random.randrange(30,60)*MILION, 
                            'seq': i}, 
                        'tags': {
                            'srcip': '10.0.10.10', 
                            'scrp': 65173, 
                            'dstip': '10.0.2.2', 
                            'dstp': 45361}, 
                        'time': timestamp+100*MILION, 
                        'measurement': 'int_telemetry'}]

    print("Write points: {0}".format(json_body))
    client.write_points(json_body)
