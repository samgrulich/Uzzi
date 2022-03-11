from email import header
import requests
from typing import Dict, List

from crossplatform import core, core_exceptions, network
from crossplatform.core_types import MarketPageAPIs, RankPageAPIs


headers = {
    # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    # 'sec-fetch-dest': 'document',
    'Accept-Encoding': 'identity',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
}

class Magiceden(core.MarketPage): 
    def __init__(self) -> None:
        super().__init__(
            "https://magiceden.io/marketplace/", # url 
            {
                MarketPageAPIs.all_collections: lambda: "https://api-mainnet.magiceden.io/all_collections?edge_cache=true",
                MarketPageAPIs.collection_floor: lambda collection: f"https://api-mainnet.magiceden.io/rpc/getCollectionEscrowStats/{collection}?edge_cache=true ",
                MarketPageAPIs.collection_info: lambda collection: f"https://api-mainnet.magiceden.io/collections/{collection}?edge_cache=true",
                MarketPageAPIs.snapshot_query: lambda collection: 'https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q={"$match":{"collectionSymbol":"' + collection + '"},"$sort":{"createdAt":-1},"$skip":0,"$limit":20}',
                MarketPageAPIs.nft_querry: lambda nftId: f"https://magiceden.io/item-details/{nftId}"
            } # apis  
            )

    def get_snapshot(self, collectionId: str, rankId: str) -> core.Snapshot:
        if not self._check_collection(collectionId):
            raise Exception("Not valid collection")

        # get collection data from internet
        url = self.apis[MarketPageAPIs.snapshot_query](collectionId)

        response = network.recursive_get(url, limit=3, pause=0, headers=headers)        

        if response.status_code != 200 and (response.status_code > 399 or response.status_code < 300):
            raise core_exceptions.NetworkError(f"Couldn't reach collection, code: {response.status_code}, url: {url}")

        data = response.json()["results"]

        self.rankPage = Howrare()

        nfts = list(map(
            lambda nft_dict : 
                core.NFT(
                nft_dict["id"],
                nft_dict["title"],
                nft_dict["mintAddress"],
                nft_dict["price"],
                nft_dict["img"],
                # nft_dict["rarity"],
                self.rankPage.get_rank(rankId, nft_dict["title"]),
                nft_dict["attributes"]
            ), 
            data
        ))

        newSnap = core.Snapshot(nfts)
        self.lastSnap[collectionId] = newSnap
        result = (newSnap - self.lastSnap[collectionId]) if collectionId in self.lastSnap.keys() else newSnap

        return result

# private:
    def _parse_collections(self) -> List[str]:
        url = self.apis[MarketPageAPIs.all_collections]()

        response = network.recursive_get(url, limit=3, headers=headers)        

        if response.status_code != 200 and (response.status_code > 399 or response.status_code < 300) :
            raise core_exceptions.NetworkError(f"Couldn't reach all market collections, code: {response.status_code}, url: {url}")

        data = response.json()["collections"] # list of dictionaries
        collections = list(map(lambda collection_dict: collection_dict["symbol"] , data))

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

        response = network.recursive_get(url, limit=3, headers=headers)

        if response.status_code != 200 and (response.status_code > 399 or response.status_code < 300) :
            raise core_exceptions.NetworkError(f"Couldn't reach all rank collections, code: {response.status_code}, url: {url}")

        data = response.json()["result"]["data"] # list of dictionaries
        collections = list(map(lambda collection_dict: collection_dict["url"][1:].lower() , data))

        return collections

    def _get_collection_data(self, collectionId: str) -> dict:
        # get collection ranks
        response = requests.get(self.apis[RankPageAPIs.collection_rate](collectionId), headers=headers)

        if response.status_code != 200 and (response.status_code > 399 or response.status_code < 300) :
            raise core_exceptions.NetworkError("collection request failed")

        data = response.json()["result"]["data"]

        ranks = {nft_dict["link"].split('/')[-1] : nft_dict["rank"] for nft_dict in data["items"]} # extract id: rank dict from collection data

        return {"id": collectionId, "data": data["collection"], "ranks": ranks}
