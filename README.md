# Monitoring Home

I'd like to gather information about home situations.

## Architecture

Basically, a server executes a script to gather data from the Nature Remo API once per minute.

And the data fetched from there will be stored in a database named influxDB.

### Materials

- [InfluxDB](https://www.influxdata.com/get-influxdb/)
- [Nature Remo Cloud API](https://developer.nature.global/en/)
  - How to calculate the energy consumption
    - [Nature Remo Cloud API - Energy API](https://developer.nature.global/docs/how-to-calculate-energy-data-from-smart-meter-values/)
- [Grafana](https://grafana.com/grafana/)

## Environment

| Key | Value | Description |
| --- | ----- | ----------- |
| INFLUXDB_DB | database_name | the name of the database |
| INFLUXDB_USER | user_name | the name of the user |
| INFLUXDB_USER_PASSWORD | user_password | the password of the user |
| INFLUXDB_BUCKET | bucket_name | the name of the bucket |
| INFLUXDB_ORG | org_name | the name of the organization |
| INFLUXDB_TOKEN | token | the token to access the database |
| REMO_TOKEN | token | the token to access the Nature Remo API |

## How to use

### 1. Set up the environment

In advance, you need to pick up the token from the Nature Remo Cloud API and set up the environment variables.

But, `INFLUX_XXX` is not necessary to set up first, please add dummy data to environment values because these should be got from the InfluxDB.

### 2. Run the server

```bash
$ git clone https://github.com/paveg/monitoring-home.git
$ cd monitoring-home
$ docker-compose up -d
```
