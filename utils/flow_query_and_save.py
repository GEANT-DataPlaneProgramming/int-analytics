from influxdb import InfluxDBClient
import time
import pandas as pd
from pprint import pprint
import pickle
import pandas as pd 
from datetime import datetime, timedelta
import os

host = 'hs-04.ipa.psnc.pl'
port = 8086
"""Instantiate a connection to the InfluxDB."""
user = 'root'
password = 'root'
dbname = 'int_telemetry_db'
dbuser_password = 'my_secret_password'

client = InfluxDBClient(host, port, user, password, dbname)


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


def get_flow_from_influx(flow, duration, starttime=''):
    if flow is None:
        return []
    timestamp = time.time()
    src_ip, dst_ip = flow.split('_')
    influxdb = InfluxDBClient(host=host, port=port, username=user, password=password, database=dbname)
    if starttime == "":
        q = '''SELECT * FROM int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' and time > now() - %ss''' % (src_ip, dst_ip, duration)
    else:
        endtime = datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S") + timedelta(seconds=duration)
        q = '''SELECT * FROM int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' and time > '%s' and time < '%s' ''' % (src_ip, dst_ip, starttime+'Z', endtime.isoformat()+'Z')
    print(q)
    query_resp = influxdb.query(q)
    int_reports = list(query_resp.get_points())
    pprint(int_reports[0])
    print("query time is", time.time()-timestamp)
    print("Numer of points queries", len(int_reports))
    return int_reports
    
    
def save(flow, starttime, duration, int_reports):
    filename = "flow_%s_%s_%ssec.csv" % (flow, starttime.replace(':', '.'), duration)
    df = pd.DataFrame(int_reports) 
    df.to_csv(filename, index=False)
    os.system("zip %s %s" % (filename.replace('csv', 'zip'), filename))
    os.system("rm %s" % filename)
    
    
    
starttime = "2020-12-08T17:20:00"
#starttime = datetime.utcnow().isoformat()
#flow="150.254.169.196_195.113.172.46"
flow="217.77.95.213_195.113.172.46"
duration=60*10 #seconds
step = 1 #second

_starttime = starttime
while duration > 0:
    int_reports = get_flow_from_influx(flow, step, _starttime)
    save(flow, _starttime, duration, int_reports)
    _starttime = datetime.strptime(_starttime, "%Y-%m-%dT%H:%M:%S") + timedelta(seconds=step)
    _starttime = _starttime.isoformat()
    duration -= step
    
    
    
    



