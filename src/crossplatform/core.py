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
class Collection: pass
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
        if not ids:
            ids = [nft.id for nft in data]
        
        self.list = data
        self.ids = ids

    def __sub__(self, other: "Snapshot") -> "Snapshot":
        """
        Get the difference between two Snapshots
        """
        final_ids = list(filter(lambda id: not id in other.ids, self.ids))
        final_list = [self.list[self.ids.index(id)] for id in final_ids]

        return Snapshot(final_list, final_ids)

    def isEmpty(self) -> bool:
        return not len(self.list) 


class Collection:
    """
    Class used for nft collection parsing from web

    Attributes
    ----------
    id : str
        id of collection at marketplace

    Methods
    -------
    get_snapshot() - get difference between the last snapshot and this one

    """
    def __init__(self, collectionId: str, name: str, ranks: Dict[str, int]) -> None:
        self.id = collectionId
        self.name = name
        self.lastSnap = None
        self.ranks = ranks

    def get_rank(self, nftId: str) -> int:
        nftId = nftId.split('#')[-1]

        if not nftId in self.ranks.keys():
            raise core_exceptions.NotValidQuerry(f"{self.name}; {nftId}")

        return self.ranks[nftId]

    def get_snapshot(self, newSnap: Snapshot) -> Snapshot: 
        result = newSnap - self.lastSnap
        self.lastSnap = newSnap 

        return result


class Page:
    """
    Class used to store and change data from Website

    To initialize:
    --------------

    request(self) -> str
    parse(self, key: str) -> str

    _parse_collections(self) -> List[str]

    """

    def __init__(self, url: str, apis: Dict[int, Callable] = None) -> None:
        self.url = f'{url}/'
        self.apis = apis
        self.collections = self._parse_collections()
    
    def request(self) -> str: raise core_exceptions.NotInitialized("Page: request")
    def parse(self, key: str): raise core_exceptions.NotInitialized("Page: parse")
    
# private: 
    def _parse_collections(self) -> List[str]: raise core_exceptions.NotInitialized("Page: _parse_collections")
    def _check_collection(self, collectionId: str): return collectionId in self.collections


class MarketPage(Page):
    def __init__(self, url: str, apis: Dict[int, Callable] = None) -> None:
        super().__init__(url, apis)

    def get_snapshot(self, collectionId: str) -> Snapshot: raise core_exceptions.NotInitialized("MarketPage: get_snapshot")


class RankPage(Page):
    def __init__(self, url: str, apis: Dict[int, Callable] = None) -> None:
        super().__init__(url, apis)

        self.collections_data = { } # dict [collectionId, collection obj]

    def get_rank(self, collection: str or Collection, nftId: str) -> int: 
        if type(collection) == Collection: # use the passed collection
            return collection.get_rank(nftId)
        
        if not collection in self.collections:
            raise core_exceptions.NotValidQuerry(collection)

        if not collection in self.collections_data.keys(): # get collection from local storage
            coll_data = self.get_collection_data(collection)
        else:
            coll_data = self.collections_data[collection]
        
        return coll_data.get_rank(nftId)
        

    def get_collection_data(self, collectionId: str) -> Collection:
        # get collection object from id
        if not collectionId in self.collections:
            raise core_exceptions.NotValidQuerry(collectionId)
        
        if collectionId in self.collections_data.keys():
            return self.collections_data[collectionId]

        collection = self._get_collection_data(collectionId)
        self.collections_data[collectionId] = collection

        return collection

# private: 
    def _get_collection_data(self, collectionId: str) -> Collection: pass
