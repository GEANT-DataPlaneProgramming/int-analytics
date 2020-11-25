from influxdb import InfluxDBClient
import time
import pandas as pd
import numpy as np
from pprint import pprint
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime, timedelta

host = 'hs-04.ipa.psnc.pl'
port = 8086
user = 'root'
password = 'root'
dbname = 'int_telemetry_db'
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
        q = '''SELECT * FROM int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' and time > now() - %sms''' % (src_ip, dst_ip, duration)
    else:
        endtime = datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f") + timedelta(milliseconds=duration)
        q = '''SELECT * FROM int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' and time > '%s' and time < '%s' ''' % (src_ip, dst_ip, starttime+'Z', endtime.isoformat()+'Z')
    print(q)
    query_resp = influxdb.query(q)
    int_reports = list(query_resp.get_points())
    pprint(int_reports[0])
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
                                                #marker_color=np.array(delays),
                                                #marker_colorscale=["blue", "green", "red"], # 'Rainbow',
                                                marker_size=2)
    )
    fig.update_layout(
        title="Timestamps difference",
        xaxis_title="time",
        yaxis_title="diff (ms)",
        yaxis_tickformat='.1e',
        template='plotly_white', #'simple_white'
    )
    print("scatter time is", time.time()-timestamp)
    filename = "%s_%sms_flow_delay.png" % (starttime.replace(':', '.'), duration)
    pio.write_image(fig, filename, scale=8)
    print("png time is", time.time()-timestamp)
    
    fig = go.Figure(data = go.Histogram( 
            x = np.array(delays),
            nbinsx=100)
    )
    fig.update_layout(
        title="Timestamps difference histogram",
        xaxis_title="diff (ms)",
        yaxis_title="count",
        xaxis_tickformat='.1e',
        template='plotly_white', #'simple_white'
    )
    print("scatter time is", time.time()-timestamp)
    filename = "%s_%sms_flow_delay_hist.png" % (starttime.replace(':', '.'), duration)
    pio.write_image(fig, filename, scale=4)
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
                                                marker_size=2)
    )
    fig.update_layout(
        title="Packet Inter-Arrival Time",
        xaxis_title="Time",
        yaxis_title="IAT (ms)",
        template='plotly_white', #'simple_white'
    )
    print("scatter time is", time.time()-timestamp)
    filename = "%s_%sms_flow_iat.png" % (starttime.replace(':', '.'), duration)
    pio.write_image(fig, filename, scale=8)
    print("png time is", time.time()-timestamp)
    
    
    fig = go.Figure(data = go.Histogram( 
            x = np.array(jitter[1:]),
            nbinsx=100)
    )
    fig.update_layout(
        title="Packet Inter-Arrival Time histogram",
        xaxis_title="IAT (ms)",
        yaxis_title="count",
        yaxis_type="log",
        template='plotly_white', #'simple_white'
    )
    print("scatter time is", time.time()-timestamp)
    filename = "%s_%sms_flow_iat_hist.png" % (starttime.replace(':', '.'), duration)
    pio.write_image(fig, filename, scale=4)
    print("png time is", time.time()-timestamp)
  
# https://plotly.com/python/static-image-export/
#https://plotly.com/python/datashader/


starttime = "2020-11-25T8:10:00.00"
#starttime = datetime.utcnow().isoformat()
#flow="150.254.169.196_195.113.172.46"
flow="217.77.95.213_195.113.172.46"
duration=1000    #miliseconds
int_reports = get_flow_from_influx(flow=flow, duration=duration, starttime=starttime)
#int_reports = get_flow_from_influx(flow=flow, duration=duration)
if len(int_reports) > 0:
    create_delay(int_reports, flow, starttime, duration)
    create_jitter(int_reports, flow, starttime, duration)