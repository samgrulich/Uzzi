from asyncore import loop
from urllib import response
import requests
import time

def recursive_get(url: str, limit: int = 5, pause: float = 1, **kwargs) -> requests.Response:
    response = requests.get(url, **kwargs)
    loopCount = 0

    while response.status_code != 200 and loopCount < limit: 
        response = requests.get(url, **kwargs)
        loopCount += 1

        time.sleep(pause)

    return response
