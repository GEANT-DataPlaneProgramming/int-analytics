from influxdb import InfluxDBClient
import time
import pandas as pd
import pprint

host = 'hs-04.ipa.psnc.pl'
port = 8086

user = 'root'
password = 'gn4intp4'
dbname = 'int_telemetry_db'

client = InfluxDBClient(host, port, user, password, dbname)

select1 = """
SELECT mean("delay") AS "mean_delay", mean("sink_jitter") AS "mean_jitter", mean("reordering") AS "mean_reordering"
INTO "int_averaged_100ms"
FROM "int_telemetry"
WHERE srcip = '217.77.95.213' AND dstip = '195.113.172.46' 
GROUP BY time(100ms)
"""

select2 = """
SELECT count("dstts") AS "pps" 
INTO int_averaged_100ms
FROM int_telemetry
WHERE srcip = '217.77.95.213' AND dstip = '195.113.172.46' 
GROUP BY time(1s)
"""

#client.drop_continuous_query(name='cq_int_fbk_100ms', database='int_telemetry_db')
#client.create_continuous_query(name="cq_int_fbk_100ms", select=select1, database="int_telemetry_db", resample_opts="EVERY 50ms FOR 200ms")
#client.create_continuous_query(name="cq_int_fbk_pps", select=select2, database="int_telemetry_db", resample_opts=None)

time.sleep(1)
print("\n")
pprint.pprint(client.get_list_continuous_queries())