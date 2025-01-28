import logging
import requests

def make_api_get_request(url, headers=None, params=None, timeout=10):
    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error("API GET request failed: %s", e)
        return None

def make_api_post_request(url, headers=None, json=None, timeout=10):
    try:
        response = requests.post(url, headers=headers, json=json, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error("API POST request failed: %s", e)
        return None