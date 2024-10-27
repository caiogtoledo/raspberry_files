import os
import json
from time import sleep
import datetime
import socket
from ina219 import INA219
import requests
from concurrent.futures import ThreadPoolExecutor
import requests.exceptions

base_url_local = 'http://localhost:8080'
base_url_cloud = 'https://solarsystemapi-production.up.railway.app'
backup_file = 'falhas.json'

ina_battery = INA219(shunt_ohms=0.1, max_expected_amps=0.6, address=0x41)
ina_battery.configure(voltage_range=ina_battery.RANGE_16V,
                      gain=ina_battery.GAIN_AUTO,
                      bus_adc=ina_battery.ADC_128SAMP,
                      shunt_adc=ina_battery.ADC_128SAMP)

ina_solar_panel = INA219(shunt_ohms=0.1, max_expected_amps=0.6, address=0x44)
ina_solar_panel.configure(voltage_range=ina_solar_panel.RANGE_16V,
                          gain=ina_solar_panel.GAIN_AUTO,
                          bus_adc=ina_solar_panel.ADC_128SAMP,
                          shunt_adc=ina_solar_panel.ADC_128SAMP)

ina_consumer_1 = INA219(shunt_ohms=0.1, max_expected_amps=0.6, address=0x45)
ina_consumer_1.configure(voltage_range=ina_consumer_1.RANGE_16V,
                         gain=ina_consumer_1.GAIN_AUTO,
                         bus_adc=ina_consumer_1.ADC_128SAMP,
                         shunt_adc=ina_consumer_1.ADC_128SAMP)

ina_consumer_2 = INA219(shunt_ohms=0.1, max_expected_amps=0.6, address=0x40)
ina_consumer_2.configure(voltage_range=ina_consumer_2.RANGE_16V,
                         gain=ina_consumer_2.GAIN_AUTO,
                         bus_adc=ina_consumer_2.ADC_128SAMP,
                         shunt_adc=ina_consumer_2.ADC_128SAMP)


def check_internet_connection():
    try:
        socket.create_connection(("www.google.com", 80), timeout=5)
        return True
    except OSError:
        return False


def save_failed_request(url, payload):
    """Salva a requisição que falhou em um arquivo local."""
    failed_request = {"url": url, "payload": payload}

    if os.path.exists(backup_file):
        with open(backup_file, 'r') as file:
            data = json.load(file)
    else:
        data = []

    data.append(failed_request)

    with open(backup_file, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Falha salva em backup: {url}")


def post_request(url, payload):
    """Envia uma requisição POST e salva em backup caso falhe."""
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Levanta exceções para códigos HTTP 4xx/5xx
        print(f"POST to {url}: Status Code {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"Connection error when sending POST to {url}")
        save_failed_request(url, payload)
    except requests.exceptions.Timeout:
        print(f"Timeout error when sending POST to {url}")
        save_failed_request(url, payload)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error when sending POST to {url}: {http_err}")
        save_failed_request(url, payload)
    except Exception as e:
        print(f"General error when sending POST to {url}: {e}")
        save_failed_request(url, payload)


try:
    while True:
        # Bateria
        payload_battery = {
            "battery_id": "1",
            "soc": ina_battery.voltage() / 4.2,
            "voltage": ina_battery.voltage(),
            "current": ina_battery.current(),
            "temperature": 25.0,  # fictício
            "timestamp": int(datetime.datetime.now().timestamp()) * 1000
        }
        print('-----------------------------')
        print('Bateria')
        print(payload_battery)

        # Placa solar
        payload_solar_panel = {
            "solar_panel_id": "12",
            "instantly": ina_solar_panel.power()/1000,
            "timestamp": int(datetime.datetime.now().timestamp()) * 1000
        }
        print('-----------------------------')
        print('Placa solar')
        print(payload_solar_panel)

        # Consumidor 1
        payload_consumer_1 = {
            "consumer_id": "1",
            "instantly": ina_consumer_1.power()/1000,
            "timestamp": int(datetime.datetime.now().timestamp()) * 1000
        }
        print('-----------------------------')
        print('Consumidor 1')
        print(payload_consumer_1)

        # Consumidor 2
        payload_consumer_2 = {
            "consumer_id": "2",
            "instantly": ina_consumer_2.power()/1000,
            "timestamp": int(datetime.datetime.now().timestamp()) * 1000
        }
        print('-----------------------------')
        print('Consumidor 2')
        print(payload_consumer_2)

        # URLs da API
        urls = {
            'battery_local': f'{base_url_local}/measure-battery',
            'solar_panel_local': f'{base_url_local}/measure-solar-panel',
            'consumer_1_local': f'{base_url_local}/measure-consumer',
            'consumer_2_local': f'{base_url_local}/measure-consumer',

            'battery_cloud': f'{base_url_cloud}/measure-battery',
            'solar_panel_cloud': f'{base_url_cloud}/measure-solar-panel',
            'consumer_1_cloud': f'{base_url_cloud}/measure-consumer',
            'consumer_2_cloud': f'{base_url_cloud}/measure-consumer',
        }

        with ThreadPoolExecutor() as executor:
            executor.submit(
                post_request, urls['battery_local'], payload_battery)
            executor.submit(
                post_request, urls['solar_panel_local'], payload_solar_panel)
            executor.submit(
                post_request, urls['consumer_1_local'], payload_consumer_1)
            executor.submit(
                post_request, urls['consumer_2_local'], payload_consumer_2)

            if check_internet_connection():
                executor.submit(
                    post_request, urls['battery_cloud'], payload_battery)
                executor.submit(
                    post_request, urls['solar_panel_cloud'], payload_solar_panel)
                executor.submit(
                    post_request, urls['consumer_1_cloud'], payload_consumer_1)
                executor.submit(
                    post_request, urls['consumer_2_cloud'], payload_consumer_2)

        sleep(0.5)

except KeyboardInterrupt:
    print("\nCtrl-C pressionado. Programa encerrado...")
