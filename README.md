# In-band Telemetry flow monitoring analytical platform

In-band Telemetry flow monitoring analytical platform is composed of the INT database (influxDB) and INT visualisation tooling (Grafana and Plotly-based).

The INT implementation and testing was done within the GÉANT Data Plane Programmibilty activity:
* website will be published soon

## Step 1 - Run docker-compose with INT analytical platform.

### Versions

* InfluxDB:          1.8.3
* Grafana:           7.3.3

### Preconfiguration

Increase available memory for influxdb UDP buffers:

```
sudo sysctl -w net.core.rmem_default=1073741824
sudo sysctl -w net.core.rmem_max=1073741824
```

Configure the same values permamently in `/etc/sysctl.conf'
```
net.core.rmem_max=1073741824
net.core.rmem_default=1073741824
```

### Quick Start

To start INT monitoring stack for the first time create docker volumes manually and then start all defined services:

```sh
cd ./in_band_visualisation
sudo docker volume create influxdb-volume
sudo docker volume create grafana-volume
sudo docker-compose up -d
```

To stop the INT monitoring stack launch:

```sh
sudo docker-compose stop
```

### Mapped Ports

```
Host    Container   Service

3003    3000    grafana
8086    8086    influxdb
8089    8089    influxdb udp
5000    5000    plotly
```

### Grafana visualisation User Inteface

Open <http://localhost:3003>


### Plotly visualisation User Inteface

Open <http://localhost:5000>


## Step 2 - Manually configure Grafana

### Add data source on Grafana

1. Using the wizard click on `Add data source`
2. Choose a `name` for the source and flag it as `Default`
3. Choose `InfluxDB` as `type`
4. Choose `direct` as `access`
5. Fill remaining fields as follows and click on `Add` without altering other fields

```
Url:    http://localhost:8086
Database:   int_telemetry_db

Basic auth and credentials must be left unflagged. Proxy is not required.

Now you are ready to add your first dashboard and launch some query on database.

### Import Grafana dashboard

Open <http://localhost:3003>

Select home > import dashboard > Upload .json File.

Select newest `json` file from ./grafana directory.

![Alt text](flow_monitoring_grafana_dashboard.png?raw=true "Flow monitoring dashboard")

## Contact

int-discuss@lists.geant.org
