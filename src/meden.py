import requests
from typing import Dict, List

from crossplatform import core, exceptions
from crossplatform.types import MarketPageAPIs, RankPageAPIs


class Magiceden(core.MarketPage): 
    def __init__(self) -> None:
        super().__init__(
            "https://magiceden.io/marketplace/", # url 
            {
                MarketPageAPIs.all_collections: lambda : "https://api-mainnet.magiceden.io/all_collections?edge_cache=true",
                MarketPageAPIs.collection_floor: lambda collection : f"https://api-mainnet.magiceden.io/rpc/getCollectionEscrowStats/{collection}?edge_cache=true ",
                MarketPageAPIs.collection_info: lambda collection : f"https://api-mainnet.magiceden.io/collections/{collection}?edge_cache=true",
                MarketPageAPIs.snapshot_query: lambda collection : 'https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q=\{"$match":\{"collectionSymbol":"' + collection + '"\},"$sort":\{"createdAt":-1\},"$skip":0,"$limit":20}'
            } # apis  
            )

    def get_snapshot(self, collectionId: str) -> core.Snapshot:
        if not self._check_collection(collectionId):
            raise Exception("Not valid collection")

        url = self.apis[MarketPageAPIs.snapshot_query](collectionId)
        response = requests.get(url)

        if response != 200:
            raise exceptions.NetworkError(f"Couldn't reach collection, {url}")

        data = response.json()["results"]

        # TODO: parse every one of these to nft
        # add them to snapshot
        # return snapshot

        return 

# private:
    def _parse_collections(self) -> List[str]:
        url = self.apis[MarketPageAPIs.all_collections]()
        response = requests.get(url)

        if response != 200:
            raise exceptions.NetworkError(f"Couldn't reach all collections, {url}")

        data = response.json()["collections"] # list of dictionaries
        collections = list(map(lambda collection_dict: collection_dict["symbol"] , data))

        return collections

class Howrare(core.RankPage): 
    def __init__(self) -> None:
        super().__init__(
            "https://howrare.is/", # url
            {
                RankPageAPIs.all_collections: lambda : "https://howrare.is/api/v0.1/collections",
                RankPageAPIs.collection_full: lambda collection : f"https://howrare.is/api/v0.1/collections/{collection}",
                RankPageAPIs.collection_rate: lambda collection : f"https://howrare.is/api/v0.1/collections/{collection}/only_rarity"
            } #apis
            )
