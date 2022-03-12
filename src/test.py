import requests

def request(url:str, **kwargs):
    return requests.get(url, **kwargs)

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
    print("listing magiceden")
    for url in magicedenAPIS:
        response1 = request(url, headers=headers)
        response2 = request(url)
        print("response1: ", response1.status_code, ", response2: ", response2.status_code)
    
    print("listing howrare")
    for url in howrareAPIS:
        response1 = request(url, headers=headers)
        response2 = request(url)
        print("response1: ", response1.status_code, ", response2: ", response2.status_code)

    print('done')

main()