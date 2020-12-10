from influxdb import InfluxDBClient
import time
import pandas as pd
import numpy as np
from pprint import pprint
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime, timedelta
import pandas as pd 
import os

host = 'hs-04.ipa.psnc.pl'
port = 8086
user = 'root'
password = 'root'
dbname = 'int_telemetry_db'
dbuser = 'int'
dbuser_password = 'my_secret_password'

pio.kaleido.scope.default_width = 1000
pio.kaleido.scope.default_height = 0.6 * pio.kaleido.scope.default_width

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
    
def get_flow_rate_from_influx(flow, duration, starttime=''):
    if flow is None:
        return []
    timestamp = time.time()
    src_ip, dst_ip = flow.split('_')
    influxdb = InfluxDBClient(host=host, port=port, username=user, password=password, database=dbname)
    if starttime == "":
        q = ''' SELECT count("dstts") FROM int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' AND  time > now() - %sms GROUP BY time(1ms)  ''' % (src_ip, dst_ip, duration)
    else:
        endtime = datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%S.%f") + timedelta(milliseconds=duration)
        q = ''' SELECT count("dstts") FROM int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' AND  time > '%s' and time < '%s' GROUP BY time(1ms)  ''' % (src_ip, dst_ip, starttime+'Z', endtime.isoformat()+'Z')
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
    min_delay = min(delays)
    max_dalay = max(delays)
    shift = 10 #(max_dalay - min_delay)/10.0
    delays = [d - min_delay + shift for d in delays]
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
        #yaxis_tickformat='.1e',
        template='plotly_white', #'simple_white'
    )
    print("scatter time is", time.time()-timestamp)
    filename = "%s_%sms_flow_delay.png" % (starttime.replace(':', '.'), duration)
    pio.write_image(fig, filename, scale=4)
    print("png time is", time.time()-timestamp)
    
    fig = go.Figure(data = go.Histogram( 
            x = np.array(delays),
            nbinsx=100)
    )
    fig.update_layout(
        title="Timestamps difference histogram",
        xaxis_title="diff (ms)",
        yaxis_title="count",
        #xaxis_tickformat='.1e',
        template='plotly_white', #'simple_white'
    )
    print("scatter time is", time.time()-timestamp)
    filename = "%s_%sms_flow_delay_hist.png" % (starttime.replace(':', '.'), duration)
    pio.write_image(fig, filename, scale=1)
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
        xaxis_title="time",
        yaxis_title="IAT (ms)",
        template='plotly_white', #'simple_white'
    )
    print("scatter time is", time.time()-timestamp)
    filename = "%s_%sms_flow_iat.png" % (starttime.replace(':', '.'), duration)
    pio.write_image(fig, filename, scale=4)
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
    pio.write_image(fig, filename, scale=1)
    print("png time is", time.time()-timestamp)
    
    
    
    
def create_ipvd(int_reports, flow, starttime, duration):
    timestamp = time.time()
    delays = [(r['dstts'] - r['origts'])/MILION for r in int_reports]
    last_delay = 0
    ipvd = []
    for d in delays:
        ipvd.append(d - last_delay)
        last_delay = d
        
    fig = go.Figure(data = go.Scatter(
                                                x= get_datatime(int_reports),
                                                y= np.array(ipvd[1:]),
                                                mode='markers',
                                                #marker_color=np.array(delays),
                                                #marker_colorscale=["blue", "green", "red"], # 'Rainbow',
                                                marker_size=2)
    )
    fig.update_layout(
        title="Packet Delay Variation (PDV)",
        xaxis_title="time",
        yaxis_title="PDV (ms)",
        template='plotly_white', #'simple_white'
    )
    print("scatter time is", time.time()-timestamp)
    filename = "%s_%sms_flow_pvd.png" % (starttime.replace(':', '.'), duration)
    pio.write_image(fig, filename, scale=2)
    print("png time is", time.time()-timestamp)
    
    fig = go.Figure(data = go.Histogram( 
            x = np.array(ipvd[1:]),
            nbinsx=100)
    )
    fig.update_layout(
        title="Packet Delay Variation histogram",
        xaxis_title="PDV (ms)",
        yaxis_title="count",
        #xaxis_tickformat='.1e',
        template='plotly_white', #'simple_white'
    )
    print("scatter time is", time.time()-timestamp)
    filename = "%s_%sms_flow_dpv_hist.png" % (starttime.replace(':', '.'), duration)
    pio.write_image(fig, filename, scale=1)
    print("png time is", time.time()-timestamp)
    
 
def create_packet_rate(flow, duration, starttime):
    int_reports = get_flow_rate_from_influx(flow, duration, starttime)
    timestamps = [r['time'] for r in int_reports]
    rates = [r['count'] for r in int_reports]
    timestamp = time.time()
   
    fig = go.Figure(data = go.Scatter(
                                                x= timestamps,
                                                y= np.array(rates),
                                                mode='markers',
                                                marker_size=2)
    )
    fig.update_layout(
        title="Packet rate",
        xaxis_title="time",
        yaxis_title="Pkt/ms",
        template='plotly_white'
    )
    print("scatter time is", time.time()-timestamp)
    filename = "%s_%sms_flow_rate.png" % (starttime.replace(':', '.'), duration)
    pio.write_image(fig, filename, scale=1)
    print("png time is", time.time()-timestamp)
        
    save(flow+"_rate",  starttime, duration, int_reports)

    
def save(flow, starttime, duration, int_reports):
    filename = "flow_%s_%s_%sms.csv" % (flow, starttime.replace(':', '.'), duration)
    df = pd.DataFrame(int_reports) 
    df.to_csv(filename, index=False)
    os.system("zip %s %s" % (filename.replace('csv', 'zip'), filename))
    os.system("rm %s" % filename)

  
# https://plotly.com/python/static-image-export/
#https://plotly.com/python/datashader/


for duration in [1000*60]:
    starttime = "2020-12-08T17:30:00.00"
    #starttime = datetime.utcnow().isoformat()
    #flow="150.254.169.196_195.113.172.46"
    flow="217.77.95.213_195.113.172.46"
    #duration=1000    #miliseconds
    #int_reports = get_flow_from_influx(flow=flow, duration=duration, starttime=starttime)
    #int_reports = get_flow_from_influx(flow=flow, duration=duration)
    create_packet_rate(flow, duration, starttime)
    #if len(int_reports) > 0:
        #save(flow, starttime, duration, int_reports)
        #~ create_delay(int_reports, flow, starttime, duration)
        #~ create_jitter(int_reports, flow, starttime, duration)
        #~ create_ipvd(int_reports, flow, starttime, duration)

