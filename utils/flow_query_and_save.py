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
dbname = 'int_telemetry_db'
dbuser_password = 'my_secret_password'

client = InfluxDBClient(host, port, user, password, dbname)

#srcip = '150.254.169.196'
srcip = '217.77.95.213'
dstip = '195.113.172.46'


def check_missing_entries(samples):
    prev_seq = 0
    sum_missing = 0
    for index, element in enumerate(samples):
        seq = int(element['seq'])
        t = element['time']
        diff = seq - prev_seq 
        if diff != 1:
            print("Missing entry at index {}, diff is {}, seq value is {}, prev seq is {}, timestamp is {}".format(index, diff, seq, prev_seq, t))
            if index != 0:
                sum_missing += diff - 1
        prev_seq = seq

    print('Sum of missing seq is {0} ({1:.3f}%)'.format(sum_missing, 100.0*sum_missing/len(samples)))

starttime = datetime.utcnow().isoformat()
print(starttime)
duration = '3m'

q = '''SELECT * FROM int_telemetry WHERE "srcip" = '%s' AND "dstip" = '%s' ORDER BY time DESC LIMIT 100000''' % (srcip, dstip)
q = '''SELECT * FROM int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' and time > '2020-09-03T07:18:41.16Z' and time < '2020-09-03T07:18:41.18Z' ''' % (srcip, dstip)
q = '''SELECT seq FROM int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' and time > now() - %s''' % (srcip, dstip, duration)
#q = '''SELECT * FROM int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' ''' % (srcip, dstip)
query_resp = client.query(q)

samples = list(query_resp.get_points())
print(len(samples))
print(samples[0])

check_missing_entries(samples)


filename = "flow_%s_%s_%s_%s.csv" % (srcip, dstip, starttime.replace(':', '.'), duration)

df = pd.DataFrame(samples) 

#print(df)
df.to_csv(filename, index=False)

#with open(filename, 'wb') as f:
#    pickle.dump(samples, f)



