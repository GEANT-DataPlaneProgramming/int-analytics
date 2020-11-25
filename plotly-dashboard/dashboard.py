from flask import Flask, render_template, request, send_file
import plotly
import plotly.graph_objs as go
import sys
import pandas as pd
import numpy as np
import json
import copy
import pickle
import logging
import time
import threading
from datetime import datetime, timedelta
from influxdb import InfluxDBClient

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("dasboard")

app = Flask(__name__)
timeseries = {}
INFLUX_IP = "localhost"
INFLUX_PORT = 8086
INFLUX_USERNAME = 'int'
INFLUX_PASSWD = 'xxx'
INFLUX_DATABASE = 'int_telemetry_db'

def get_srcip_from_influx():
    logger.debug('Getting Src IPs from influxDB')
    influxdb = InfluxDBClient(host=INFLUX_IP, port=INFLUX_PORT, username=INFLUX_USERNAME, password=INFLUX_PASSWD, database=INFLUX_DATABASE)
    query_resp = influxdb.query('''SHOW TAG VALUES FROM int_telemetry WITH KEY = "srcip"''')
    values = list(query_resp.get_points())
    values = [v['value'] for v in values] 
    logger.debug("srcip are %s", str(values))
    return values[:100]
    
def get_dstip_from_influx():
    logger.debug('Getting Dst IPs from influxDB')
    influxdb = InfluxDBClient(host=INFLUX_IP, port=INFLUX_PORT, username=INFLUX_USERNAME, password=INFLUX_PASSWD, database=INFLUX_DATABASE)
    query_resp = influxdb.query('''SHOW TAG VALUES FROM int_telemetry WITH KEY = "dstip"''')
    values = list(query_resp.get_points())
    values = [v['value'] for v in values] 
    logger.debug("dstip are %s", str(values))
    return values[:100]
    
def get_flows_from_influx():
    flows = []
    src_ips = get_srcip_from_influx()
    for dst_ip in get_dstip_from_influx():
        for src_ip in src_ips:
            flows.append({
                                    'id': "%s_%s" % (src_ip, dst_ip),
                                    'text': "src IP %s, dst IP %s" % (src_ip, dst_ip)
                                    }
            )
    return flows
    
def get_flow_from_influx(flow, duration, starttime):
    if flow is None:
        return []
    try:
        src_ip, dst_ip = flow.split('_')
        influxdb = InfluxDBClient(host=INFLUX_IP, port=INFLUX_PORT, username=INFLUX_USERNAME, password=INFLUX_PASSWD, database=INFLUX_DATABASE)
        if starttime == "":
            q = '''SELECT * FROM iint_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' and time > now() - %sms''' % (src_ip, dst_ip, duration)
        else:
            endtime = datetime.strptime(starttime, "%Y-%m-%dT%H:%M") + timedelta(milliseconds=int(duration))
            q = '''SELECT * FROM int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' and time > '%s' and time < '%s' ''' % (src_ip, dst_ip, starttime+':00Z', endtime.isoformat()+'Z')
        #q = '''SELECT * FROM int_telemetry.flow_monitoring_policy.int_telemetry WHERE "srcip" = '%s' and "dstip" = '%s' ORDER BY time DESC LIMIT 100000''' % (src_ip, dst_ip)
        logger.debug(q)
        query_resp = influxdb.query(q)
        int_reports = list(query_resp.get_points())
        return int_reports
    except Exception as e:
        logger.exception(e)
        return []

def calculate_delay(int_reports):
    delays = [(r['dstts'] - r['origts'])/MILION for r in int_reports]
    return np.array(delays)
    
def calculate_jitter(int_reports):
    last_dstts = 0
    jitter = []
    for r in int_reports:
        jitter.append(r['dstts']/MILION - last_dstts)
        last_dstts = r['dstts']/MILION
    return np.array(jitter[1:])
    
def calculate_reordering(int_reports):
    last_seq = 0
    reordering = []
    for r in int_reports:
        reordering.append(r['seq'] - last_seq)
        last_seq = r['seq']
    return np.array(reordering[1:])
    
def get_datatime(int_reports):
        #timestamps = [r['time'] for r in int_reports]
        #timestamps = pd.to_datetime(timestamps[1:], unit='ns')
        if len(int_reports) == 0:
            return []
        timestamps = [r['dstts'] for r in int_reports]
        timestamps = pd.DataFrame(timestamps, dtype='float64')
        return timestamps[0].astype('datetime64[ns]').tolist()
        
    
@app.route('/')
def index():
    return render_template('index.html', delay=create_delay(),
                                                            delay_hist=create_delay_hist(),
                                                            jitter=create_jitter(),
                                                            jitter_hist=create_jitter_hist(),
                                                            reordering=create_reordering())
MILION = 1000000.0

data_loaded = threading.Event()
INT_reports = None
# https://plotly.com/python-api-reference/generated/plotly.graph_objects.Scattergl.html
# https://plotly.com/python/colorscales/
# https://plotly.com/python/builtin-colorscales/
    

    
@app.route('/delay', methods=['GET', 'POST'])
def create_delay():
    try:
        timestamp = time.time()
        flow = request.args.get('selected')
        duration = request.args.get('duration')
        starttime = request.args.get('startdate')
        if flow == None:
            return json.dumps([], cls=plotly.utils.PlotlyJSONEncoder)
        logger.debug("flow %s", flow)
        int_reports = get_flow_from_influx(flow, duration, starttime)
        global INT_reports
        INT_reports = int_reports
        data_loaded.set()
        logger.debug("Influx query time is %s", time.time()-timestamp)
        data = [go.Scattergl( # go.Scglattergl
            x= get_datatime(int_reports),
            y= calculate_delay(int_reports),
            mode='markers',
            marker_size=3
        )]
        logger.debug("Scattergl time is %s", time.time()-timestamp)
        j = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
        logger.debug("json time is %s", time.time()-timestamp)
        return j
    except Exception as e:
        logger.exception(e)
        return json.dumps([], cls=plotly.utils.PlotlyJSONEncoder)
     
             

@app.route('/delay_hist', methods=['GET', 'POST'])
def create_delay_hist():
    try:
        flow = request.args.get('selected')
        if flow == None:
            return json.dumps([], cls=plotly.utils.PlotlyJSONEncoder)
        data_loaded.wait()        
        data = [go.Histogram( 
            x = calculate_delay(INT_reports),
            nbinsx=100,
        )]
        j = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
        return j
    except Exception as e:
        logger.exception(e)
        return json.dumps([], cls=plotly.utils.PlotlyJSONEncoder)
    
@app.route('/jitter', methods=['GET', 'POST'])
def create_jitter():
    try:
        flow = request.args.get('selected')
        if flow == None:
            return json.dumps([], cls=plotly.utils.PlotlyJSONEncoder)
        data_loaded.wait()
        data = [go.Scattergl(
            x= get_datatime(INT_reports), 
            y= calculate_jitter(INT_reports),
            mode='markers',
            #marker_color=np.array(jitter[1:]),
            #marker_colorscale=["blue", "green", "red"], # 'Rainbow',
            marker_size=3
        )]
        data_loaded.clear()
        return json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        logger.exception(e)
        return json.dumps([], cls=plotly.utils.PlotlyJSONEncoder)

        
@app.route('/jitter_hist', methods=['GET', 'POST'])
def create_jitter_hist():
    try:
        flow = request.args.get('selected')
        if flow == None:
            return json.dumps([], cls=plotly.utils.PlotlyJSONEncoder)
        data_loaded.wait()
        data = [go.Histogram( 
            x = calculate_jitter(INT_reports),
            nbinsx=100,
        )]
        data_loaded.clear()
        return json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        logger.exception(e)
        return json.dumps([], cls=plotly.utils.PlotlyJSONEncoder)


@app.route('/reordering', methods=['GET', 'POST'])
def create_reordering():
    try:
        flow = request.args.get('selected')
        if flow == None:
            return json.dumps([], cls=plotly.utils.PlotlyJSONEncoder)
        data_loaded.wait()
        data = [go.Scattergl(
            x= get_datatime(INT_reports), 
            y= calculate_reordering(INT_reports),
            mode='markers',
            #marker_color=np.array(reordering[1:]),
            #marker_colorscale=["blue", "green", "red"],
            marker_size=3
        )]
        data_loaded.clear()
        return json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        logger.exception(e)
        return json.dumps([], cls=plotly.utils.PlotlyJSONEncoder)
        
@app.route('/list', methods=['GET', 'POST'])
def devices():
    try:
        data = get_flows_from_influx()
        return  json.dumps(data)
    except Exception as e:
        logger.exception(e)
    
if __name__ == '__main__':
    if len(sys.argv) == 2:
        INFLUX_IP = sys.argv[1]
    logger.info("INFLUX_IP is %s", INFLUX_IP)
    
    app.run(host='0.0.0.0' , port=5000)
    #print(get_flows_from_influx())
    #get_flow_from_influx(source="10.0.10.10_10.0.2.2", duration=10)