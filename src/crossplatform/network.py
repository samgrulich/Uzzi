import requests
import time
import threading

from typing import List
from crossplatform.debug import debug_print


proxies = [] # list of ip addresses in strings 
requestCount = 0

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


# TODO: check if the path is valid
def load_proxies(file_path: str) -> List[str]:
    global proxies

    with open(file_path, "r") as f:
        for line in f.readlines():
            proxies.append(line[:-1]) 


def proxy_request(url: str, **kwargs) -> requests.Response:
    global proxies
    global requestCount

    proxyIndex = requestCount % len(proxies)
    proxy = proxies[proxyIndex].split(":")
    proxyIP = f"{proxy[0]}:{proxy[1]}"

    proxy_dict = {
        "http":  proxyIP, 
        "https": proxyIP
    }

    with threading.Lock():
        requestCount += 1
        
    return requests.get(url, proxies=proxy_dict, **kwargs)


