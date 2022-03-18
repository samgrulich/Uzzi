import time
import requests
from crossplatform import network


magicedenAPIS = \
[
    "https://api-mainnet.magiceden.io/all_collections?edge_cache=true",
    "https://api-mainnet.magiceden.io/rpc/getCollectionEscrowStats/bohemia_?edge_cache=true ",
    "https://api-mainnet.magiceden.io/collections/bohemia_?edge_cache=true",
    'https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q={"$match":{"collectionSymbol":"bohemia_"},"$sort":{"createdAt":-1},"$skip":0,"$limit":20}',
    # "https://magiceden.io/item-details/{nftId}"
] # apis  

howrareAPIS = \
[
    "https://howrare.is/api/v0.1/collections",
    "https://howrare.is/api/v0.1/collections/bohemia",
    "https://howrare.is/api/v0.1/collections/bohemia/only_rarity"
] #apis
    
headers = {
    # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    # 'sec-fetch-dest': 'document',
    'Accept-Encoding': 'identity',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
}

def main():
    print("requesting meden")
    collectionData = requests.get(magicedenAPIS[0], headers=headers).json()["collections"]
    collections = [collection["symbol"] for collection in collectionData[:20]]


    for i in range(100):
        
        for i, collection in enumerate(collections):
            startTime = time.time_ns()
            url = 'https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q={"$match":{"collectionSymbol":"' + collection + '"},"$sort":{"createdAt":-1},"$skip":0,"$limit":20}'

            response1 = requests.get(url, headers=headers)
            response2 = network.safe_get(url, headers=headers)

            if response1.status_code != 200 or response2.status_code != 200:
                print("response1: ", response1.status_code, ", response2: ", response2.status_code)

            print("delta time: ", (time.time_ns() - startTime) / 10e9, " s, ", i)

    print('done')

# network.load_proxies("proxies.txt")
# main()

for i in range(10):
    startTime = time.time_ns()

    time.sleep(i)

    deltaTime = time.time_ns() - startTime

    print(deltaTime)

