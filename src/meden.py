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

        self.rankPage = Howrare()

        nfts = list(map(
            lambda nft_dict : 
                core.NFT(
                nft_dict["id"],
                nft_dict["title"],
                nft_dict["price"],
                nft_dict["img"],
                nft_dict["escrow_pubkey"],
                self.rankPage.get_rank(collectionId, nft_dict["title"]),
                nft_dict["attributes"]
            )
        ))

        return core.Snapshot(nfts) 

# private:
    def _parse_collections(self) -> List[str]:
        url = self.apis[MarketPageAPIs.all_collections]()
        response = requests.get(url)

        if response.status_code != 200:
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

# private: 
    def _get_collection_data(self, collectionId: str) -> core.Collection:
        # get collection ranks
        response = requests.get(self.apis[RankPageAPIs.collection_rate](collectionId))

        if response.status_code != 200:
            raise exceptions.NetworkError("collection request failed")

        data = response.json()["result"]["data"]

        ranks = {nft_dict["name"] : nft_dict["rank"] for nft_dict in data["items"]} # extract id: rank dict from collection data

        return core.Collection(collectionId, data["collection"], ranks)
