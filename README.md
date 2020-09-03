# Flow monitoring 

## Step 1 - Run Docker Image with Telegraf (StatsD), InfluxDB and Grafana

### Versions

* Docker Image:      2.3.0
* Ubuntu:            18.04
* InfluxDB:          1.7.10
* Telegraf (StatsD): 1.13.3-1
* Grafana:           6.6.2

### Quick Start

To start the container the first time launch:

```sh
docker run --ulimit nofile=66000:66000 \
  -d \
  --name docker-statsd-influxdb-grafana \
  -p 3003:3003 \
  -p 3004:8888 \
  -p 8086:8086 \
  -p 8125:8125/udp \
  samuelebistoletti/docker-statsd-influxdb-grafana:latest
```

To stop the container launch:

```sh
docker stop docker-statsd-influxdb-grafana
```

To start the container again launch:

```sh
docker start docker-statsd-influxdb-grafana
```

### Mapped Ports

```
Host		Container		Service

3003		3003			grafana
3004		8888			influxdb-admin (chronograf)
8086		8086			influxdb
8125		8125			statsd
```

### InfluxDB

Web Interface

Open <http://localhost:3004>

```
Username: root
Password: root
Port: 8086
```

### Grafana

Open <http://localhost:3003>

```
Username: root
Password: root
```

### Add data source on Grafana

1. Using the wizard click on `Add data source`
2. Choose a `name` for the source and flag it as `Default`
3. Choose `InfluxDB` as `type`
4. Choose `direct` as `access`
5. Fill remaining fields as follows and click on `Add` without altering other fields

```
Url: http://localhost:8086
Database:	telegraf
User: telegraf
Password:	telegraf
```

Basic auth and credentials must be left unflagged. Proxy is not required.

Now you are ready to add your first dashboard and launch some query on database.

## Step 2 - Generate traffic flow

Run the "flow_generator.py" file from the current directory.

Example output:

![Alt text](flow_generator.png?raw=true "Flow Generator")

## Step 3 - Import Grafana dashboard

Open <http://localhost:3004>

Select home > import dashboard > Upload .json File.

Select the "Flow Monitoring-1580215648269.json" file from the current directory.

In the upper right corner set the following time period: 2020-01-20 10:23:30 - 2020-01-20 10:24:50.

You should see the final result as shown below.

![Alt text](flow_monitoring_grafana_dashboard.png?raw=true "Flow monitoring dashboard")
