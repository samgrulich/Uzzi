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
        Is website supported or not (ex. support=True=Supported)
    id : str
        Id of website (ex. Google)
    valid : bool
        Same as support, with additional None check

    Methods
    -------
    get_support() -> bool:
        Check support

    get_nft_url(nft_id) -> str:
        Get url of nft details page

    export(nft_data) -> ???:
        This is the most customized method, this is called for 
        extraction data of nft_data from website 

    """

    def __init__(self, collection_id: str, url: str, id: str = 'None', nft_url: str=None) -> None:
        """
        Parameters
        ----------
        collection_id : str
            Id of collection page will use
        url : str
            URL of website page will use
        id : str - Optional
            ID of page (ex. Google)
        nft_url : str - Optional
            URL for getting nft info
        """

        self.url = f'{url}/{collection_id}'
        self.nft_url = nft_url if nft_url else self.url
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

    def get_nft_url(self, nft_id: str or int) -> str:
        """
        Get url of nft details, returns string
        """

        return f'{self.nft_url}/{nft_id}'

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
        Check validity of page

        Returns
        -------
        bool
            is page supported
        """
        # if self.support is None:
        #     return False

        return self.support


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
        """
        Get supported page object
        
        Returns
        -------
        Page
            supported page, `None` if not valid
        """
        if not self.valid:
            return None

        return self.pages[self.supported_index]

    @property
    def valid(self) -> bool:
        """
        Check if this tuple is valid
        
        Returns
        -------
        bool
            validity of page
        """
        if len(self.pages) == 0:
            return False

        if self.supported_index is None:
            index = self.get_support()
            self.supported_index = index

            return index is not None

        return True


class Collection:
    """
    Class used for nft collection parsing from web

    Attributes
    ----------
    id : str
        id of collection at marketplace
    url : str
        url of api nft getter (without id)
    valid : bool
        is collection valid
    collection_tuple : PageTuple
        pages that collection will be parsed from
    rank_tuple : PageTuple
        pages where the collection will get rank of nfts
    rarity_tuple : RarityTuple
        pages where are rarities of nft attributes

    Methods
    -------
    parse_nft(raw_nft) -> NFT
        raw_nft to nft object
    get_rank(nft_id) -> int
        rank of nft
    get_rarities(atts) -> dict
        rarities of given attributes

    """
    def __init__(self, url: str, collection_id: str, collection_tuple: PageTuple, rank_tuple: PageTuple, rarity_tuple: PageTuple) -> None:
        """
        Arguments
        ---------
        url : str
            url of market api nft getter
        collection_id : str
            id of collection at marketplace
        collection_tuple : PageTuple
            tuple of marketplaces
        rank_tuple : PageTuple
            tuple of rank getting pages
        rarity_tuple : PageTuple
            tuple of att rarity getters
        """
        # TODO: add table support
        
        self.id = collection_id
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
    def valid(self) -> bool:
        "Check validity of this collection"
        return self.collection_tuple.valid


class Snapshot:
    """
    Snapshot of active page on market page
    
    Attributes
    ----------
    list : list[dict]
        list of raw nfts
    ids : list[int]
        list of ids of nfts in self.list

    Methods
    -------
    __sub__(other: Snapshot) -> Snapshot
        removes all equal objects
    """

    def __init__(self, data: list[dict], ids: list[int] = None) -> None:
        """
        Arguments
        ---------
        data : list[dict]
            list of raw nfts
        ids : list[int] (Optional)
            list of ids of nfts, it's optional
        """
        self.list = data

        if not ids:
            ids = [nft['id'] for nft in data]
        self.ids = ids

    def __sub__(self, other: "Snapshot") -> "Snapshot":
        """
        Get the difference between two lists

        Returns
        -------
        Snapshot
            objetcs which are only in the first snapshot
        """
        final_ids = list(filter(lambda id: not id in other.ids, self.ids))
        final_list = [self.list[self.ids.index(id)] for id in final_ids]

        return Snapshot(final_list, final_ids)
