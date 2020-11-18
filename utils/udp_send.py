import socket
from influxdb import InfluxDBClient
import time


client = InfluxDBClient(host='localhost', use_udp=True, udp_port=8089)


TIMESTAMP_0 =  1000*1000*int(time.time()) # in us
CNT = 10
print("\nLoading database with %d entries\n" % CNT)

                                    
line_body = []
for i in range(CNT):
    line_body.append("int,srcip=10.0.0.1,dstip=10.0.0.2,sctp=1111,dstp=80 seq=%d,srcts=%d,dstts=%d,delay=%d,sink_jitter=%d,reordering=0 %d" % 
                                    (i, TIMESTAMP_0 + i, TIMESTAMP_0 + i + 1, i ,i, TIMESTAMP_0 + i+1))

client.send_packet(line_body, time_precision='u',protocol='line')