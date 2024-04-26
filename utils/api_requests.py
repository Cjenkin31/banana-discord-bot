import logging
import requests

def make_api_get_request(url, headers=None, params=None):
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"API GET request failed: {e}")
        return None

def make_api_post_request(url, headers=None, json=None):
    try:
        response = requests.post(url, headers=headers, json=json)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"API POST request failed: {e}")
        return None
