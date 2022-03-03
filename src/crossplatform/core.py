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
    Interface, stores data about collection, access to some handy functions

"""

import requests
from typing import List, Dict


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


class Collection:
    """
    Class used for nft collection parsing from web

    Attributes
    ----------
    id : str
        id of collection at marketplace
    marketPage : MarketPage
        object of the market web
    rankPage : RankPage
        object of the ranking page

    Methods
    -------
    get_snapshot() - get difference between the last snapshot and this one

    """
    def __init__(self, collectionId: str, filters: dict, marketPage: MarketPage, rankPage: RankPage) -> None:
        self.id = collectionId
        self.filters = filters
        self.lastSnap = None
        
        self.marketPage = marketPage
        self.rankPage = rankPage

    def get_snapshot(self, new_snap: Snapshot) -> Snapshot: 
        # TODO: difference between the two snapshots, then save this snap as last one 
        
        pass


class Page:
    """
    Class used to store and change data from Website
    """

    def __init__(self, url: str, apis: Dict[str, str] = None) -> None:
        self.url = f'{url}/'
        self.apis = apis
    
    def request(self) -> str: pass

    def get_support(self) -> bool:
        """
        Check if the page is aviable
        """

        # TODO: try to reach the website, then check the response
            
        pass

    @property
    def valid(self) -> bool:
        """
        Check if the page is aviable
        """

        return self.support
        
