from influxdb import InfluxDBClient
from influxdb_client import InfluxDBClient, Point
import time
import pandas as pd
import pprint

host = 'hs-04.ipa.psnc.pl'
port = 8086
"""Instantiate a connection to the InfluxDB."""
user = 'root'
password = 'gn4intp4'
dbname = 'int_telemetry'

client = InfluxDBClient(host, port, user, password, dbname)
client.create_retention_policy('int_udp_policy', '7d', 1, database=None, default=True, shard_duration=u'0s')
#client.alter_retention_policy('int_policy', database='int_telemetry', duration='7d', replication=1, default=None, shard_duration=None)
print('measurements', client.get_list_measurements())
print('retention_policies', client.get_list_retention_policies('int_telemetry'))
print('series', client.get_list_series('int_telemetry', measurement='int_telemetry'))

q = '''SELECT * FROM int_telemetry.int_policy.int_telemetry WHERE "srcip" = '%s' AND "dstip" = '%s' ORDER BY time DESC LIMIT 100000''' % ("150.254.169.196", "195.113.172.46")
#q = '''SELECT * FROM int_telemetry.flow_monitoring_policy.int_telemetry WHERE "srcip" = '10.0.10.10' and "dstip" = '10.0.2.2' and time > '2020-09-03T07:18:41.16Z' and time < '2020-09-03T07:18:41.18Z' '''
#q = '''SELECT * FROM int_telemetry.flow_monitoring_policy.int_telemetry WHERE time > now() - 1s'''
q = '''SELECT * FROM int_telemetry.int_policy.int_telemetry WHERE "srcip" = '%s' AND "dstip" = '%s' ORDER BY time DESC LIMIT 1000''' % ("217.77.95.213", "195.113.172.46")
q = '''SELECT delay FROM int_telemetry WHERE "srcip" =~ /'%s'/ AND "dstip" =~ /'%s'/ LIMIT 100000''' % ("217.77.95.213", "195.113.172.46")
q = '''SELECT * FROM int_telemetry WHERE "srcip" =~ /'%s'/ AND "dstip" =~ /'%s'/ LIMIT 100000''' % ("10.0.0.1", "10.0.0.2")
q = '''SELECT * FROM int_telemetry LIMIT 100'''
print(q)
query_resp = client.query(q)

samples = list(query_resp.get_points())
print(len(samples))
print(samples[:10])