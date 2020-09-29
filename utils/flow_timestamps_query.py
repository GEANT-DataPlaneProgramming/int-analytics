from influxdb import InfluxDBClient
import time
import pandas as pd
import pprint

host = 'hs-04.ipa.psnc.pl'
port = 8086
"""Instantiate a connection to the InfluxDB."""
user = 'root'
password = 'root'
dbname = 'int_telemetry'
dbuser = 'int'
dbuser_password = 'my_secret_password'

client = InfluxDBClient(host, port, user, password, dbname)

q = '''SELECT * FROM int_telemetry.flow_monitoring_policy.int_telemetry WHERE "srcip" = '%s' AND "dstip" = '%s' ORDER BY time DESC LIMIT 100000''' % ("150.254.169.196", "195.113.172.46")
#q = '''SELECT * FROM int_telemetry.flow_monitoring_policy.int_telemetry WHERE "srcip" = '10.0.10.10' and "dstip" = '10.0.2.2' and time > '2020-09-03T07:18:41.16Z' and time < '2020-09-03T07:18:41.18Z' '''
#q = '''SELECT * FROM int_telemetry.flow_monitoring_policy.int_telemetry WHERE time > now() - 1s'''
query_resp = client.query(q)

samples = list(query_resp.get_points())
print(len(samples))
pprint.pprint(samples[:20])

for diff_type in ['origts', 'dstts']:
    print(diff_type)
    last_timestamp = 0
    time_diffs = []
    for s in samples[-9:-4]:
        time_diffs.append(last_timestamp - s[diff_type])
        print(s[diff_type], time_diffs[-1])
        last_timestamp = s[diff_type]
        
    print(pd.Series(time_diffs[1:]).describe())