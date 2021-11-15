"Group of universal object (everything extracted from internet should be parsed into these)"

import requests


class NFT:
    "NFT class for unifying nft objects"

    def __init__(self, id: str, name: str, token: str, price: float, image: str, rank: int, attributes: str) -> None:
        self.id = id
        self.name = name
        self.price = price
        self.img = image
        self.token = token
        self.rank = rank
        self.atts = attributes

    # public

    def vars(self) -> dict:
        "Get dictionary of variables"
        return vars(self)


class Page:
    def __init__(self, collection: str, url: str, id: str = 'None') -> None:
        self.url = f'{url}/{collection}'
        self.support = self.get_support()
        self.id = id

    def get_support(self) -> bool:
        "Check if collection / given url exists"
        try:
            response = requests.get(f'{self.url}')
            return response.status_code == 200
        except:
            return False

    def export(self, data):
        return None

    @property
    def valid(self) -> bool:
        "Check validity of page"
        if self.support is None:
            return False

        return True


class PageTuple:
    def __init__(self, page_types: list[type], collection: str) -> None:
        self.pages = [page_type(collection) for page_type in page_types]
        self.supported_index = self.get_support()

    def get_support(self) -> int:
        "Get index of first supported page, if not supported returns `None`"
        support = None

        for i, page in enumerate(self.pages):
            if page.support:
                support = i
                break

        return support

    def export(self, data):
        "Export data from supported page"
        if not self.valid:
            return None

        return self.supported_page.export(data)

    @property
    def supported_page(self) -> Page:
        "Get supported page as type Page, returns `None` if not valid"
        if self.valid:
            return None

        self.pages[self.supported_page]
        pass

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
