from influxdb import InfluxDBClient
import time
import random


host = 'hs-04.ipa.psnc.pl'
port = 8086
"""Instantiate a connection to the InfluxDB."""
user = 'root'
password = 'root'
dbname = 'int_telemetry_db'

client = InfluxDBClient(host, port, user, password, dbname)


timestamp = int(time.time() * 1e9)
print('Timestamp is {0}'.format(timestamp))

line_body = [
    f'int_telemetry,srcip=150.254.169.196,dstip=195.113.172.46,srcp=4607,dstp=17000,protocol=17 origts=1619726150314693000,dstts=1619726150332779969,seq=79572,delay=18666969,sink_jitter=376835,reordering=0 {timestamp}',
    f'int_telemetry,srcip=150.254.169.196,dstip=195.113.172.46,srcp=4607,dstp=17000,protocol=17,hop_index=0 hop_delay=298000,hop_jitter=580000 {timestamp}'
    f'int_telemetry,srcip=150.254.169.196,dstip=195.113.172.46,srcp=4607,dstp=17000,protocol=17,hop_index=1 hop_delay=397000,link_delay=1170000,hop_jitter=546000 {timestamp}'
]

success = client.write_points(line_body, batch_size=1000, time_precision='u',protocol='line')
print(f"Write points successful: {success}")
