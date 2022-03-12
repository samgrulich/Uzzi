"""
Group of universal classes/interfaces
-------------------------------------

All classes in this module are designed to behave as interfaces for 
easier integration of multipage support, you can modify them but
do not have to

Classes:
--------
    Class - should be used as it is \n
    Half - can be used as it is, but you can modify it \n
    Interface - use it as base for your custom class \n

* NFT \n
    Class, stores data of your nft in cross-page/universal state
* Snapshot \n
    Class, list of downloaded nfts
* Page \n
    Interface, stores data about your website
* PageTuple \n
    Half, for grouping simillar pages together
* Collection \n
    Interface, stores data about collection, access to some handy Callables

"""

import requests

import crossplatform.core_exceptions as core_exceptions
from crossplatform.core_types import MarketPageAPIs 
from typing import List, Dict, Callable


REC_LIM = 5


class NFT: pass
class Snapshot: pass

class Page: pass
class MarketPage(Page): pass
class RankPage(Page): pass


class NFT:
    "NFT class for easier cross platforming"

    def __init__(self, id: str, name: str, token: str, price: float, image: str, rank: int, attributes: dict) -> None:
        """
        Parameters
        ----------
        id : str
            Id of nft 
        name : str
            Name of nft
        price : float
            Price/Last-Sale of nft
        image : str
            URL of nft image
        rank : int
            Rank of nft, ussually won't come with raw nft data
        attributes : dict
            Dictionary of nft's attributes (ex. {Background: Red, ..., Hat: cylinder})
        """

        self.id = id
        self.name = name
        self.price = price
        self.img = image
        self.token = token
        self.rank = rank
        self.atts = attributes


class Snapshot:
    """
    Snapshot of active page on market page
    """

    def __init__(self, data: List[NFT], ids: List[str] = None) -> None:        
        if not len(data):
            ids = []
        
        if not ids:
            ids = [nft.id for nft in data]
        
        self.list = data
        self.ids = ids

    def __sub__(self, other: "Snapshot") -> "Snapshot":
        """
        Get the difference between two Snapshots
        """
        idsFinal = list(filter(lambda id: not id in other.ids, self.ids))
        listFinal = [self.list[self.ids.index(id)] for id in idsFinal]

        # TODO: check the price update

        return Snapshot(listFinal, idsFinal)

    def isEmpty(self) -> bool:
        return not len(self.list) 


class Page:
    """
    Class used to store and change data from Website

    To initialize:
    --------------

    request(self) -> str
    parse(self, key: str) -> str

    _parse_collections(self) -> List[str]

    """

    def __init__(self, url: str, apis: Dict[int, Callable] = { }) -> None:
        self.url = f"{url}/" if not url[-1] == '/' else url 
        self.apis = apis

        collections = self._parse_collections()
        self.collections = collections if collections else []
    
    def request(self) -> str: raise core_exceptions.NotInitialized("Page: request")
    def parse(self, key: str): raise core_exceptions.NotInitialized("Page: parse")
    
# private: 
    def _parse_collections(self) -> List[str]: raise core_exceptions.NotInitialized("Page: _parse_collections")
    def _check_collection(self, collectionID: str): return collectionID in self.collections


class MarketPage(Page):
    def __init__(self, url: str, apis: Dict[int, Callable] = { }) -> None:
        super().__init__(url, apis)

        self.lastSnap = { }

    def get_snapshot(self, collectionId: str) -> Snapshot: raise core_exceptions.NotInitialized("MarketPage: get_snapshot")


class RankPage(Page):
    def __init__(self, url: str, apis: Dict[int, Callable] = None) -> None:
        super().__init__(url, apis)

        self.collectionsData = { } # dict [collectionId, collection obj]

    def get_rank(self, collection: str or Dict, nftId: str) -> int: 
        if type(collection) == dict: # use the passed collection
            return collection.get_rank(nftId)

        coll_data = self.get_collection_data(collection)
        
        # TODO: check this func for errors
        def get_rank(nftID: str) -> int:
            nftID = nftID.split('#')[-1]

            if not nftID in coll_data["ranks"].keys():
                collectionID = coll_data["data"]["name"]
                raise core_exceptions.NotValidQuerry(f"{collectionID}; {nftID}")

            return coll_data["ranks"][nftID]

        return get_rank(nftId)

    def get_collection_data(self, collectionID: str) -> Dict:
        # get collection object from id
        if not collectionID in self.collections:
            raise core_exceptions.NotValidQuerry(collectionID)
        
        if collectionID in self.collectionsData.keys():
            return self.collectionsData[collectionID]

        collection = self._get_collection_data(collectionID)
        self.collectionsData[collectionID] = collection

        return collection


# private: 
    def _get_collection_data(self, collectionId: str) -> Dict: pass
