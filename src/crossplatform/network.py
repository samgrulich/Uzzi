import requests
import time
import threading

from typing import List
from requests.auth import HTTPProxyAuth
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
    response = proxy_get(url, **kwargs)
    loopCount = 0
    
    while response.status_code != 200 and (response.status_code == 429 and loopCount >= limit):
        print(f"{loopCount}: server returned code: {response.status_code}, trying again")
        response = proxy_get(url, **kwargs)
        
        if response.status_code == 429:
            waitTime = int(response.headers["Retry-After"])
            waitTime = waitTime if waitTime else 1

            for i in range(0, waitTime):
                time.sleep(1)
                
                if not i % 15:
                    print(f"{i}/{waitTime}")

        loopCount += 1

    if response.status_code != 200:
        debug_print(f"finished with code: {response.status_code}, after: {loopCount} tries")

    return response

def proxy_get(url: str, **kwargs):
    global proxies
    global requestCount

    proxyIndex = requestCount % len(proxies)

    with threading.Lock():
        requestCount += 1
    
    print("requesting ", url)
    print("  with proxy: ", proxies[proxyIndex]["http"])

    return requests.get(url, proxies=proxies[proxyIndex], **kwargs)

# TODO: check if the path is valid
def load_proxies(file_path: str):
    global proxies
    global session
        
    with open(file_path, "r") as f:
        for line in f.readlines():
            data = line.replace('\n', '')
            data = f"http://{data}/"
            proxies.append({"http": data, "https": data})

    print(proxies)


def request(url: str, **kwargs) -> requests.Response:
    """
    For public use, when you need to switch type of request just edit the body of this function
    """

    return safe_get(url, **kwargs)
