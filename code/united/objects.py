"""
Group of universal classes/interfaces
-------------------------------------

All classes in this module are designed to behave as interfaces for 
easier integration of multipage support, you can modify them but
you can use them as they are

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


class NFT:
    "NFT class for easier cross platforming"

    def __init__(self, id: str, name: str, token: str, price: float, image: str, rank: int, attributes: str) -> None:
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
        attributes : str
            String dictionary of nft's attributes (ex. 'Background: Red, ..., Hat: cylinder')
        """
        # TODO: atts aren't so much united

        self.id = id
        self.name = name
        self.price = price
        self.img = image
        self.token = token
        self.rank = rank
        self.atts = attributes

    # public

    def vars(self) -> dict:
        """
        Get dictionary of variables

        Same as using 'vars(this_obj)', parses vars of this object to string

        Returns
        -------
        dict
            This object's vars parsed into dictionary
        """
        return vars(self)


class Page:
    """
    Class used to store and change data from Website

    Attributes
    ----------
    url : str
        Url of website + collection `doesn't` have '/' at the end
    support : bool
        Is website supported or not (ex. True=Supported)
    id : str
        Id of website (ex. Google)
    valid : bool
        Same as support, with additional None check

    Methods
    -------
    get_support() -> bool:
        Check support

    export(nft_data) -> ???:
        This is the most customized method, this is called for 
        extraction data of nft_data from website 

    """

    def __init__(self, collection_id: str, url: str, id: str = 'None') -> None:
        """
        Parameters
        ----------
        collection_id : str
            Id of collection page will use
        url : str
            URL of website page will use
        id : str
            ID of page (ex. Google)
        """
        # BUG: is .valid needed??

        self.url = f'{url}/{collection_id}'
        self.support = self.get_support()
        self.id = id

    def get_support(self) -> bool:
        """
        Check if collection / given url exists

        Returns
        -------
        bool
            is page aviable
        """

        # TODO: make it request again
        try:
            response = requests.get(f'{self.url}')
            return response.status_code == 200
        except:
            return False

    def export(self, **nft_data):
        """
        Export data of nft from web

        Returns
        -------
        """
        return None

    @property
    def valid(self) -> bool:
        """
        Check validity of page with additional None check

        Returns
        -------
        bool
            is page supported
        """
        if self.support is None:
            return False

        return True


class PageTuple:
    """
    Class used for easier manipulation with multiple pages

    Attributes
    ----------
    pages : list[Page]
        List of pages the tuple will be using
    supported_index : int
        Index of supported page, can be None
    supported_page : Page
        Get object of supported Page, `None` if not valid
    valid : bool
        Validity of this tuple, if there's atleast one page supported

    Methods
    -------
    get_support() -> int:
        returns index of supported page, `None` if none is valid
    export(nft_data) -> ???:
        calls export of supported page


    """

    def __init__(self, page_types: list[type], collection_id: str) -> None:
        """
        Arguments
        ---------
        page_types : list[type]
            list of pages you will be using
        collection_id : str
            id of collection you want to use
        """

        self.pages = [page_type(collection_id) for page_type in page_types]
        self.supported_index = self.get_support()

    def get_support(self) -> int:
        """
        Get index of first supported page

        Returns
        -------
        int
            index of supported page,`None` if not supported
        """
        support = None

        for i, page in enumerate(self.pages):
            if page.support:
                support = i
                break

        return support

    def export(self, **nft_data):
        """
        Export data from supported page

        Arguments
        ---------
        nft_data
            nft_data needed for page to extract desired data

        Returns
        -------
        ???
            That depedns on the page (object)
        """
        if not self.valid:
            return None

        return self.supported_page.export(**nft_data)

    @property
    def supported_page(self) -> Page:
        "Get supported page as type Page, returns `None` if not valid"
        if not self.valid:
            return None

        return self.pages[self.supported_index]

    @property
    def valid(self) -> bool:
        "Check if this tuple is valid"
        if len(self.pages) == 0:
            return False

        if self.supported_index is None:
            index = self.get_support()
            return index is None

        return True


class Collection:
    def __init__(self, url: str, collection: str, collection_tuple: PageTuple, rank_tuple: PageTuple, rarity_tuple: PageTuple) -> None:
        self.id = collection
        self.url = url

        self.collection_tuple = collection_tuple
        self.rank_tuple = rank_tuple
        self.rarity_tuple = rarity_tuple

    def parse_nft(self, raw_nft: dict) -> NFT:
        "Parse raw nft to polished universal nft object"
        return None

    def get_rank(self, nft_id: int) -> int:
        "Get rank of nft, `None` if ranks aren't supported"
        if not self.rank_tuple.valid:
            return None

        return self.rank_tuple.export(nft_id)

    def get_rarities(self, atts: dict) -> dict:
        "Parse rarity/score of each attribute, `None` if didn't succeded"
        if not self.valid:
            return None

        # TODO: get rarities

        pass

    @property
    def valid(self):
        "Check validity of this collection"
        return self.collection_tuple.valid


class Snapshot:
    "Snapshot of active page on market page"

    def __init__(self, data: list[dict], ids: list[int] = None) -> None:
        self.list = data

        if not ids:
            ids = [nft['id'] for nft in data]
        self.ids = ids

    def __sub__(self, other: "Snapshot") -> "Snapshot":
        "Get the difference between two lists, returns Snapshot object"
        final_ids = list(filter(lambda id: not id in other.ids, self.ids))
        final_list = [self.list[self.ids.index(id)] for id in final_ids]

        return Snapshot(final_list, final_ids)
