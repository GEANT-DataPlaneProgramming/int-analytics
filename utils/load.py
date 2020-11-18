import argparse
import time
from statistics import mean
import struct

from multiprocessing import Process, Queue
from influxdb import InfluxDBClient

user = 'root'
password = 'root'
dbname = 'int_telemetry'
dbuser = 'int'
dbuser_password = 'my_secret_password'

#~ user = 'dpp_int'
#~ password = 'int_WP6'
#~ user = 'gint'
#~ password = 'AhyzsKHrueBY8bCGd8XTLNkj'
    
def prepare(host, port):
    client = InfluxDBClient(host, port, user, password, dbname, pool_size=10)

    print("Create database: " + dbname)
    client.create_database(dbname)

    print("Create a retention policy")
    client.create_retention_policy('awesome_policy', '3d', 3, default=True)
    
    
def single_load(host='localhost', port=8086, dst='10.0.0.1', stats_queue=None):
    """Instantiate a connection to the InfluxDB."""

    query = '''SELECT "seq" FROM "int_telemetry" WHERE "srcip" = '10.0.0.1' AND "dstip" = '10.0.0.2' '''

    FLOW1= {
                "dstip": dst,
                "dstp": 80,
                "sctp": 1111,
                "srcip": "10.0.0.1",
             }
    
    TIMESTAMP_0 =  1000*1000*int(time.time()) # in us
        
    CNT = 10
    print("\nLoading database with %d entries\n" % CNT)
    
    #~ for i in range(CNT):
        #~ json_body.append({
                                        #~ "measurement": "int",
                                        #~ "tags": FLOW1,
                                        #~ "fields": {
                                            #~ 'origts': TIMESTAMP_0,
                                            #~ 'dstts': TIMESTAMP_0 + i,
                                            #~ "delay": 10,
                                            #~ "seq"	: i, 
                                            #~ "sink_jitter": 10,
                                            #~ 'reordering':0,
                                        #~ },
                                        #~ "time":TIMESTAMP_0 + i,
                                    #~ })
                                    
    line_body = []

    for i in range(CNT):
        line_body.append("int,srcip=10.0.0.1,dstip=%s,sctp=1111,dstp=80 seq=%d,srcts=%d,dstts=%d,delay=%d,sink_jitter=%d,reordering=0 %d" % 
                                        (dst, i, TIMESTAMP_0 + i, TIMESTAMP_0 + i + 1, i ,i, TIMESTAMP_0 + i+1))

    client = InfluxDBClient(host, port, user, password, dbname, pool_size=10)

    start = time.time()
    #client.write_points(json_body, batch_size=10000, time_precision='u',protocol='json')
    client.write_points(line_body, batch_size=40000, time_precision='u',protocol='line')
    stop = time.time()-start
    #print("Write time of {0} entries is {1}".format(CNT, stop))
    #print("Write speed is:", CNT/stop)
    #print("Test ended at", time.ctime())
    stats_queue.put(CNT/stop)
    
    #~ result = client.query('SELECT COUNT(*) from "int" where dstip=$dst', bind_params={'dst':dst})
    #~ for r in result.get_points():
        #~ print(r)
        
    #client.delete_series(dbname, "int")
    
def get_stats(host, port):        
    internal_client = InfluxDBClient(host, port, user, password, '_internal', timeout=2, retries=1) #-precision 'rfc3339'
    print(internal_client.ping())
    
    query = 'select derivative(pointReq, 1s) from "write" where time > now() - 2m'
    #query = 'select pointReq from "write" where time > now() - 10s'
    result = internal_client.query(query)
    for r in result.get_points():
        print(r)
    
    #~ #result = internal_client.query("SHOW STATS FOR 'httpd'")
    #~ #for r in result.get_points():
    #~ #    print(r)
        
    
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(
        description='example code to play with InfluxDB')
    parser.add_argument('--host', type=str, required=False,
                        default='localhost',
                        help='hostname of InfluxDB http API')
    parser.add_argument('--port', type=int, required=False, default=8086,
                        help='port of InfluxDB http API')
    parser.add_argument('--dst', type=str, required=False, default="10.0.0.1",
                        help='flow destination ip address')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    args.host = 'hs-04.ipa.psnc.pl'
    #args.host = 'intcollect.gint.nmaas.eu'
    #args.host = '150.254.160.153'
    #args.port = 443
    print("\nDatabase load in last seconds before the test:")
    get_stats(args.host, args.port)
    #prepare(args.host, args.port)
    #~ f = open('results.txt', 'a')
    #~ #client_cnt = 1
    #~ #for client_cnt in range(client_cnt, client_cnt+1):
    #~ for client_cnt in range(1, 2):
        #~ print("\nStart testing influxDB load with {} clients".format(client_cnt))
        #~ stats_queue= Queue(client_cnt)
        #~ processes = []
        #~ for i in range(client_cnt):
            #~ p = Process(target=single_load, args=(args.host, args.port, args.dst, stats_queue))
            #~ p.start()
            #~ processes.append(p)
        #~ stats = []
        #~ for i in range(client_cnt):
           #~ stats.append(stats_queue.get()) 
        #~ #print(client_cnt, mean(stats))
        #~ f.write("[{}, {}]\n".format(client_cnt, mean(stats)))
        #~ for p in processes:
            #~ p.join()
        #~ time.sleep(10)
        #~ print("\nDatabase load in the last seconds (during the test):")
        #~ get_stats(args.host, args.port)
        #~ #time.sleep(3*60)
