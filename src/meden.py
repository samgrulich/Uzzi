from typing import Dict, List

from crossplatform import core, core_exceptions, network
from crossplatform.core_types import MarketPageAPIs, RankPageAPIs


headers = {
    # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    # 'sec-fetch-dest': 'document',
    # 'Accept-Encoding': 'identity',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
}

class Magiceden(core.MarketPage): 
    def __init__(self) -> None:
        super().__init__(
            "https://magiceden.io/marketplace/", # url 
            {
                MarketPageAPIs.all_collections: lambda: "https://api-mainnet.magiceden.io/all_collections?edge_cache=true",
                MarketPageAPIs.collection_floor: lambda collection: f"https://api-mainnet.magiceden.io/rpc/getCollectionEscrowStats/{collection}?edge_cache=true",
                MarketPageAPIs.collection_info: lambda collection: f"https://api-mainnet.magiceden.io/collections/{collection}?edge_cache=true",
                MarketPageAPIs.snapshot_query: lambda collection: 'https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q={"$match":{"collectionSymbol":"' + collection + '"},"$sort":{"createdAt":-1},"$skip":0,"$limit":20}',
                MarketPageAPIs.nft_querry: lambda nftId: f"https://magiceden.io/item-details/{nftId}"
            } # apis  
            )

        self.rankPage = Howrare()

    def get_snapshot(self, collectionID: str, rankID: str) -> core.Snapshot:
        if not self._check_collection(collectionID):
            raise Exception("Not valid collection")

        # get collection data from internet
        url = self.apis[MarketPageAPIs.snapshot_query](collectionID)
        response = network.safe_get(url, headers=headers)
        # response = requests.get(url, headers=headers)
        # response = network.recursive_get(url, limit=3, pause=0, headers=headers)        

        if response.status_code != 200 and (response.status_code > 399 or response.status_code < 300):
            raise core_exceptions.NetworkError(f"Couldn't reach collection, code: {response.status_code}, url: {url}")

        data = response.json()["results"]

        nfts = list(map(
            lambda nftDict : 
                core.NFT(
                nftDict["id"],
                nftDict["title"],
                nftDict["mintAddress"],
                nftDict["price"],
                nftDict["img"],
                # nft_dict["rarity"],
                self.rankPage.get_rank(rankID, nftDict["title"]),
                nftDict["attributes"]
            ), 
            data
        ))

        newSnap = core.Snapshot(nfts)
        lastSnap = self.lastSnap[collectionID] if collectionID in self.lastSnap.keys() else newSnap
        result = newSnap - lastSnap
        
        self.lastSnap[collectionID] = newSnap

        return result

# private:
    def _parse_collections(self) -> List[str]:
        url = self.apis[MarketPageAPIs.all_collections]()
        response = network.safe_get(url, headers=headers)
        # response = requests.get(url, headers=headers)
        # response = network.recursive_get(url, limit=3, headers=headers)        

        if response.status_code != 200 and (response.status_code > 399 or response.status_code < 300) :
            raise core_exceptions.NetworkError(f"Couldn't reach all market collections, code: {response.status_code}, url: {url}")

        data = response.json()["collections"] # list of dictionaries
        collections = list(map(lambda collectionDict: collectionDict["symbol"] , data))

        return collections

class Howrare(core.RankPage): 
    def __init__(self) -> None:
        super().__init__(
            "https://howrare.is/", # url
            {
                RankPageAPIs.all_collections: lambda: "https://howrare.is/api/v0.1/collections",
                RankPageAPIs.collection_full: lambda collection: f"https://howrare.is/api/v0.1/collections/{collection}",
                RankPageAPIs.collection_rate: lambda collection: f"https://howrare.is/api/v0.1/collections/{collection}/only_rarity"
            } #apis
            )

# private: 
    def _parse_collections(self) -> List[str]:
        url = self.apis[RankPageAPIs.all_collections]()
        response = network.safe_get(url)
        # response = requests.get(url)
        # response = network.recursive_get(url, limit=3)

        if response.status_code != 200:
            raise core_exceptions.NetworkError(f"Couldn't reach all rank collections, code: {response.status_code}, url: {url}")

        data = response.json()["result"]["data"] # list of dictionaries
        collections = list(map(lambda collectionDict: collectionDict["url"][1:].lower() , data))

        return collections

    def _get_collection_data(self, collectionID: str) -> dict:
        # get collection ranks
        url = self.apis[RankPageAPIs.collection_rate](collectionID)
        response = network.safe_get(url)
        # response = requests.get(url)

        if response.status_code != 200:
            raise core_exceptions.NetworkError("Howrare collection request failed")

        data = response.json()["result"]["data"]

        ranks = {nftDict["link"].split('/')[-1] : nftDict["rank"] for nftDict in data["items"]} # extract id: rank dict from collection data

        return {"id": collectionID, "data": data["collection"], "ranks": ranks}
