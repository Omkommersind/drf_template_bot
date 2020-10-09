import sys
import time
import requests
import urllib.error
import urllib.parse


def exponential_backoff_request(method: str, url: str, headers: dict=None, params: dict=None, data: dict=None):
    if headers is None:
        headers = {}
    if params is None:
        params = {}

    params = urllib.parse.urlencode(params)
    if len(params) > 0:
        url = f"{url}?{params}"

    current_delay = 0.1
    max_delay = 5

    print('Executing api request...')
    print(url)

    while True:
        try:
            response = requests.request(method, url, headers=headers, params=params, data=data)

            if response.status_code not in range(200, 299):
                return response
        except urllib.error.URLError:
            pass
        else:
            return response

        if current_delay > max_delay:
            sys.exit('External service not responded')

        time.sleep(current_delay)
        current_delay *= 2
