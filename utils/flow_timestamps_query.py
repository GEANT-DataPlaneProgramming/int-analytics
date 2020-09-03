from influxdb import InfluxDBClient
import time
import pandas as pd

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
#"dstts", "origts"
q = '''SELECT * FROM int_telemetry.flow_monitoring_policy.int_telemetry WHERE "srcip" = '%s' AND "dstip" = '%s' ORDER BY time DESC LIMIT 100000''' % ("10.0.10.10", "10.0.2.2")
q = '''SELECT * FROM int_telemetry.flow_monitoring_policy.int_telemetry WHERE "srcip" = '10.0.10.10' and "dstip" = '10.0.2.2' and time > '2020-08-25T07:00:00Z' and time < '2020-08-25T07:00:16Z' '''
query_resp = client.query(q)

samples = list(query_resp.get_points())
print(len(samples))
#print(samples[0])

#~ diff_type = 'origts' # 'dstts'
#~ last_timestamp = 0
#~ time_diffs = []
#~ for s in samples:
    #~ time_diffs.append(last_timestamp - s[diff_type])
    #~ print(time_diffs[-1])
    #~ last_timestamp = s[diff_type]
    
#~ print(pd.Series(time_diffs[1:]).describe())