import requests
import time
import threading

from typing import List
from requests.auth import HTTPProxyAuth
from src.crossplatform.debug import debug_print


proxies = [] # list of ip addresses in strings 
requestCount = 0
session = requests.Session()

def recursive_get(url: str, limit: int = 5, pause: float = 1, **kwargs) -> requests.Response:
    response = requests.get(url, **kwargs)
    loopCount = 0

    while response.status_code != 200 and loopCount < limit: 
        response = requests.get(url, **kwargs)
        loopCount += 1

        time.sleep(pause)

    return response

def safe_get(url: str, limit: int = 5, **kwargs) -> requests.Response:
    response = proxy_request(url, **kwargs)
    loopCount = 0
    
    while response.status_code != 200 and response.status_code == 429 and loopCount < limit:
        print(f"{loopCount}: server returned code: {response.status_code}, trying again")
        response = proxy_request(url, **kwargs)
        
        if response.status_code == 429:
            wait_time = response.headers["Retry-After"]
            wait_time = wait_time if wait_time else 1000

            time.sleep(int(wait_time) / 1000)

        loopCount += 1

    if response.status_code != 200:
        debug_print(f"finished with code: {response.status_code}, after: {loopCount} tries")

    return response


# TODO: check if the path is valid
def load_proxies(file_path: str):
    global proxies
    global session

    with open(file_path, "r") as f:
        for line in f.readlines():
            proxyList = line[:-1].split(':')
            proxyData = f"{proxyList[0]}:{proxyList[1]}"
            proxies.append(proxyData) 

    proxies = [{"http": proxy, "hppts": proxy} for proxy in proxies]
    
    auth = HTTPProxyAuth(proxyList[2], proxyList[3])
    session.proxies = proxies[0]
    session.auth = auth

    print(proxies)


def proxy_request(url: str, **kwargs) -> requests.Response:
    global proxies
    global requestCount

    proxyIndex = requestCount % len(proxies)
    proxy = proxies[proxyIndex]

    with threading.Lock():
        requestCount += 1
        
    return requests.get(url, proxies=proxy, **kwargs)


