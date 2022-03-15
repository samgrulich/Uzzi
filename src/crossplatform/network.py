from concurrent.futures import wait
import requests
import time

from crossplatform.debug import debug_print


def recursive_get(url: str, limit: int = 5, pause: float = 1, **kwargs) -> requests.Response:
    response = requests.get(url, **kwargs)
    loopCount = 0

    while response.status_code != 200 and loopCount < limit: 
        response = requests.get(url, **kwargs)
        loopCount += 1

        time.sleep(pause)

    return response

def safe_get(url: str, limit: int = 5, **kwargs) -> requests.Response:
    response = requests.get(url, **kwargs)
    loopCount = 0
    
    while response.status_code != 200 and loopCount < limit:
        print(f"{loopCount}: server returned code: {response.status_code}, trying again")
        response = requests.get(url, **kwargs)
        
        if response.status_code == 429:
            wait_time = response.headers["Retry-After"]
            wait_time = wait_time if wait_time else 1000

            time.sleep(int(wait_time) / 1000)

        loopCount += 1

    if response.status_code != 200:
        debug_print(f"finished with code: {response.status_code}, after: {loopCount} tries")

    return response
