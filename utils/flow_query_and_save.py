from influxdb import InfluxDBClient
import time
import pandas as pd
import pprint
import pickle
from datetime import datetime
import pandas as pd 

host = 'hs-04.ipa.psnc.pl'
port = 8086
"""Instantiate a connection to the InfluxDB."""
user = 'root'
password = 'root'
dbname = 'int_telemetry'
dbuser = 'int'
dbuser_password = 'my_secret_password'

client = InfluxDBClient(host, port, user, password, dbname)

#srcip = '10.0.10.10'
#dstip = '10.0.2.2'

srcip = '150.254.169.196'
dstip = '195.113.172.46'

starttime = datetime.utcnow().isoformat()
duration = '6h'

q = '''SELECT * FROM int_telemetry.flow_monitoring_policy.int_telemetry WHERE "srcip" = '%s' AND "dstip" = '%s' ORDER BY time DESC LIMIT 100000''' % (srcip, dstip)
q = '''SELECT * FROM int_telemetry.flow_monitoring_policy.int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' and time > '2020-09-03T07:18:41.16Z' and time < '2020-09-03T07:18:41.18Z' ''' % (srcip, dstip)
q = '''SELECT * FROM int_telemetry.flow_monitoring_policy.int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' and time > now() - %s''' % (srcip, dstip, duration)
query_resp = client.query(q)

samples = list(query_resp.get_points())
print(len(samples))
print(samples[0])

filename = "flow_%s_%s_%s_%s.csv" % (srcip, dstip, starttime.replace(':', '.'), duration)

df = pd.DataFrame(samples) 

print(df)

df.to_csv(filename, index=False)

#with open(filename, 'wb') as f:
#    pickle.dump(samples, f)



