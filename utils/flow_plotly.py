from influxdb import InfluxDBClient
import time
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime, timedelta

host = 'hs-04.ipa.psnc.pl'
port = 8086
user = 'root'
password = 'root'
dbname = 'int_telemetry'
dbuser = 'int'
dbuser_password = 'my_secret_password'

client = InfluxDBClient(host, port, user, password, dbname)

def get_datatime(int_reports):
    if len(int_reports) == 0:
        return []
    timestamps = [r['dstts'] for r in int_reports]
    timestamps = pd.DataFrame(timestamps, dtype='float64')
    return timestamps[0].astype('datetime64[ns]').tolist()
    
    
def get_flow_from_influx(flow, duration, starttime=''):
    if flow is None:
        return []
    timestamp = time.time()
    src_ip, dst_ip = flow.split('_')
    influxdb = InfluxDBClient(host=host, port=port, username=user, password=password, database=dbname)
    if starttime == "":
        q = '''SELECT * FROM int_telemetry.flow_monitoring_policy.int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' and time > now() - %ss''' % (src_ip, dst_ip, duration)
    else:
        endtime = datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f") + timedelta(milliseconds=10*duration) #timedelta(milliseconds=duration)
        q = '''SELECT * FROM int_telemetry.flow_monitoring_policy.int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' and time > '%s' and time < '%s' ''' % (src_ip, dst_ip, starttime+'Z', endtime.isoformat()+'Z')
    print(q)
    query_resp = influxdb.query(q)
    int_reports = list(query_resp.get_points())
    print("query time is", time.time()-timestamp)
    print("Numer of points queries", len(int_reports))
    return int_reports

MILION = 1000000.0
def create_delay(int_reports, flow, starttime, duration):
    timestamp = time.time()
    delays = [(r['dstts'] - r['origts'])/MILION for r in int_reports]
    fig = go.Figure(data = go.Scatter(
                                                x= get_datatime(int_reports),
                                                y= np.array(delays),
                                                mode='markers',
                                                marker_color=np.array(delays),
                                                marker_colorscale=["blue", "green", "red"], # 'Rainbow',
                                                marker_size=1)
    )
    fig.update_layout(
        title="Delay",
        xaxis_title="Time",
        yaxis_title="Delay (ms)",
    )
    print("scatter time is", time.time()-timestamp)
    filename = "flow_delay_%s_%s_%ss.png" % (flow, starttime.replace(':', '.'), duration)
    pio.write_image(fig, filename, scale=16)
    print("png time is", time.time()-timestamp)
    
    fig = go.Figure(data = go.Histogram( 
            x = np.array(delays),
            nbinsx=100)
    )
    fig.update_layout(
        title="Delay histogram",
        xaxis_title="Delay (ms)",
        yaxis_title="count",
    )
    print("scatter time is", time.time()-timestamp)
    filename = "flow_delay_hist_%s_%s_%ss.png" % (flow, starttime.replace(':', '.'), duration)
    pio.write_image(fig, filename, scale=8)
    print("png time is", time.time()-timestamp)

def create_jitter(int_reports, flow, starttime, duration):
    timestamp = time.time()
    last_dstts = 0
    jitter = []
    for r in int_reports:
        jitter.append(r['dstts']/MILION - last_dstts)
        last_dstts = r['dstts']/MILION
    fig = go.Figure(data = go.Scatter(
                                                x= get_datatime(int_reports),
                                                y= np.array(jitter[1:]),
                                                mode='markers',
                                                #marker_color=np.array(jitter[1:]),
                                                #marker_colorscale=["blue"], # "green", "red"], # 'Rainbow',
                                                marker_size=1)
    )
    fig.update_layout(
        title="Jitter",
        xaxis_title="Time",
        yaxis_title="Jitter (ms)",
    )
    print("scatter time is", time.time()-timestamp)
    filename = "flow_jitter_%s_%s_%ss.png" % (flow, starttime.replace(':', '.'), duration)
    pio.write_image(fig, filename, scale=16)
    print("png time is", time.time()-timestamp)
    
    
    fig = go.Figure(data = go.Histogram( 
            x = np.array(jitter[1:]),
            nbinsx=100)
    )
    fig.update_layout(
        title="Jitter histogram",
        xaxis_title="Jitter (ms)",
        yaxis_title="count",
        yaxis_type="log"
    )
    print("scatter time is", time.time()-timestamp)
    filename = "flow_jitter_hist_%s_%s_%ss.png" % (flow, starttime.replace(':', '.'), duration)
    pio.write_image(fig, filename, scale=8)
    print("png time is", time.time()-timestamp)
  
# https://plotly.com/python/static-image-export/
#https://plotly.com/python/datashader/


starttime = "2020-11-13T12:10:00.00"
#starttime = datetime.utcnow().isoformat()
#flow="150.254.169.196_195.113.172.46"
flow="217.77.95.213_195.113.172.46"
duration=1
int_reports = get_flow_from_influx(flow=flow, duration=duration, starttime=starttime)
#int_reports = get_flow_from_influx(flow=flow, duration=duration)
if len(int_reports) > 0:
    create_delay(int_reports, flow, starttime, duration)
    create_jitter(int_reports, flow, starttime, duration)