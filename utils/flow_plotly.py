from influxdb import InfluxDBClient
import time
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime, timedelta

host = 'localhost'
port = 8086
user = 'root'
password = 'root'
dbname = 'int_telemetry'
dbuser = 'int'
dbuser_password = 'my_secret_password'

#pio.kaleido.scope.default_scale = 16

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
    src_ip, dst_ip = flow.split('_')
    influxdb = InfluxDBClient(host=host, port=port, username=user, password=password, database=dbname)
    if starttime == "":
        q = '''SELECT * FROM int_telemetry.flow_monitoring_policy.int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' and time > now() - %ss''' % (src_ip, dst_ip, duration)
    else:
        endtime = datetime.strptime(starttime, "%Y-%m-%dT%H:%M") + timedelta(seconds=duration)
        q = '''SELECT * FROM int_telemetry.flow_monitoring_policy.int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' and time > '%s' and time < '%s' ''' % (src_ip, dst_ip, starttime+':00Z', endtime.isoformat()+'Z')
    print(q)
    query_resp = influxdb.query(q)
    int_reports = list(query_resp.get_points())
    print("Numer of points queries", len(int_reports))
    return int_reports

MILION = 1000000.0
def create_delay(int_reports):
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
    print("scatter time is %s", time.time()-timestamp)
    #fig.write_image("flow_delay.png")
    pio.write_image(fig, "flow_delay.png", scale=16)
    print("png time is %s", time.time()-timestamp)

def create_jitter(int_reports):
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
                                                marker_color=np.array(jitter[1:]),
                                                marker_colorscale=["blue", "green", "red"], # 'Rainbow',
                                                marker_size=1)
    )
    fig.update_layout(
        title="Jitter",
        xaxis_title="Time",
        yaxis_title="Jitter (ms)",
    )
    print("scatter time is %s", time.time()-timestamp)
    #fig.write_image("flow_jitter.png")
    pio.write_image(fig, "flow_jitter.png", scale=16)
    print("png time is %s", time.time()-timestamp)
  
# https://plotly.com/python/static-image-export/
#https://plotly.com/python/datashader/

int_reports = get_flow_from_influx(flow="10.0.10.10_10.0.2.2", duration=100, starttime="2020-08-25T07:00")
create_delay(int_reports)
create_jitter(int_reports)