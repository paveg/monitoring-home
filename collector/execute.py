import time
from datetime import datetime,timedelta,timezone
import os
import requests
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import logging
from sys import stdout

logger = logging.getLogger("Logger")
logger.setLevel(logging.INFO)
def customTime(*args):
    return datetime.now(timezone(timedelta(hours=+9), 'GMT')).timetuple()
formatter = logging.Formatter(
    fmt='%(levelname)s : %(asctime)s : %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S %z"
)
formatter.converter = customTime
consoleHandler = logging.StreamHandler(stdout)
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)
device_api_url = 'https://api.nature.global/1/devices'
appliances_api_url = 'https://api.nature.global/1/appliances'
bearer_token = os.environ.get('REMO_TOKEN')
influxdb_url = os.environ.get('INFLUXDB_URL')
dbname = os.environ.get('INFLUXDB_DB')
dbuser = os.environ.get('INFLUXDB_USER')
dbpassword = os.environ.get('INFLUXDB_USER_PASSWORD')
bucket = os.environ.get('INFLUXDB_BUCKET')
org = os.environ.get('INFLUXDB_ORG')
influxdb_token = os.environ.get('INFLUXDB_TOKEN')

client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=org, verify_ssl=False)
write_api = client.write_api(write_options=SYNCHRONOUS)
point = Point("statuses")

headers = { 'accept': 'application/json', 'Authorization': 'Bearer ' + bearer_token}
while True:
    datestr = datetime.now(timezone(timedelta(hours=+9), 'GMT')).strftime('%Y-%m-%dT%H:%M:%SZ')
    response = requests.get(device_api_url, headers=headers)

    if response.status_code == 200:
        devices = response.json()
        for device in devices:
            device_id = device.get('id')
            device_name = device.get('name')
            newest_events = device.get('newest_events', {})
            if device_name == 'Remo':
                temperature = newest_events.get('te', {}).get('val', 'Unknown')
                humidity = newest_events.get('hu', {}).get('val', 'Unknown')
                iluminance = newest_events.get('il', {}).get('val', 'Unknown')
                np = point.field("temperature", float(temperature)).field("humidity", float(humidity)).field("iluminance", float(iluminance)).time(datestr)
                write_api.write(bucket=bucket, record=np)
                logger.info("Environment information was commited.")
            elif device_name == 'RemoElite':
                response = requests.get(appliances_api_url, headers=headers)
                if response.status_code == 200:
                    appliances = response.json()
                    for appliance in appliances:
                        if appliance.get('device', {}).get('id') == device_id:
                            e_properties = appliance.get('smart_meter', {}).get('echonetlite_properties', {})
                            # @see https://developer.nature.global/docs/how-to-calculate-energy-data-from-smart-meter-values/
                            for e_property in e_properties:
                                e_property_name = e_property.get('name')
                                if e_property_name == 'measured_instantaneous':
                                    measured_instantaneous = e_property.get('val', 'Unknown')
                                elif e_property_name == 'normal_direction_cumulative_electric_energy':
                                    normal_direction_cumulative_electric_energy = e_property.get('val', 'Unknown')
                                elif e_property_name == 'cumulative_electric_energy_unit':
                                    cumulative_electric_energy_unit = e_property.get('val', 'Unknown')
                                elif e_property_name == 'coefficient':
                                    coefficient = e_property.get('val', 'Unknown')
                                elif e_property_name == 'cumulative_electric_energy_effective_digits':
                                    cumulative_electric_energy_effective_digits = e_property.get('val', 'Unknown')
                                elif e_property_name == 'reverse_direction_cumulative_electric_energy':
                                    reverse_direction_cumulative_electric_energy = e_property.get('val', 'Unknown')
                            ep = point.field("measured_instantaneous", int(measured_instantaneous)).field("normal_direction_cumulative_electric_energy", float(normal_direction_cumulative_electric_energy)).field("cumulative_electric_energy_unit", int(cumulative_electric_energy_unit)).field("coefficient", int(coefficient)).field("reverse_direction_cumulative_electric_energy", float(reverse_direction_cumulative_electric_energy)).field("cumulative_electric_energy_effective_digits", int(cumulative_electric_energy_effective_digits)).time(datestr)
                            write_api.write(bucket=bucket, record=ep)
                            logger.info("SmartMeter information was commited.")
                else:
                    logger.warning('Failed to retrieve data: ', response.text)
            else:
                logger.warning('The data fetched from unknown device.')
    else:
        logger.warning('Failed to retrieve data: ', response.text)

    time.sleep(60)
