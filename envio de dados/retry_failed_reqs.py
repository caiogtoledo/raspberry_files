import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor
import requests.exceptions

backup_file = 'falhas.json'

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
        response.raise_for_status() 
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

def retry_failed_requests():
    """Tenta reenviar as requisições que falharam e estão no arquivo de backup em paralelo."""
    if os.path.exists(backup_file):
        with open(backup_file, 'r') as file:
            data = json.load(file)

        if len(data) > 0:
            with ThreadPoolExecutor() as executor:
                futures = []
                for request in data:
                    futures.append(executor.submit(post_request, request['url'], request['payload']))
                
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Erro ao reenviar uma requisição: {e}")
                    else:
                        data.remove(request)

            with open(backup_file, 'w') as file:
                json.dump(data, file, indent=4)
        else:
            print("Nenhuma falha salva em backup.")

retry_failed_requests()