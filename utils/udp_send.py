import socket
from influxdb import InfluxDBClient
import time


client = InfluxDBClient(host='localhost', use_udp=True, udp_port=8089)


TIMESTAMP_0 =  1000*1000*1000*int(time.time()) # in ns
CNT = 10
print("\nLoading database with %d entries\n" % CNT)

                                    
line_body = []
for i in range(CNT):
    line_body.append("int_telemetry,srcip=10.0.0.1,dstip=10.0.0.2,sctp=1111,dstp=80 seq=%d,srcts=%di,dstts=%di,delay=%di,sink_jitter=%di,reordering=0i %di" % 
                                    (i, TIMESTAMP_0 + i, TIMESTAMP_0 + i + 1, i , i, TIMESTAMP_0 + i+1))


print(line_body[0])
#~ message = '\n'.join(line_body) + '\n'
#~ sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
#~ sock.sendto(message, ('localhost', 8089))

#  data = ('\n'.join(packet) + '\n').encode('utf-8')

client.send_packet(line_body, time_precision='u',protocol='line')

#~ 1605801680000000i
#~ 1605801680000001i
#~ 1605801680000001i
#~ 1605801227270915992i,
#~ 1605801228186204176i,
#~ 1605801228186204176i