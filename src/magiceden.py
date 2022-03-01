import requests
import time
from bs4 import BeautifulSoup
from typing import List
from united import bases


# Pages
# region

# Collection
# region

class Magiceden(bases.Page):
    def __init__(self, collection: str) -> None:
        super().__init__(collection, 'https://magiceden.io/marketplace', id='Magiceden')
        self.nft_url = 'https://magiceden.io/item-details'

    def get_nft_url(self, nft_id: str or int):
        return f"{self.nft_url}/{nft_id}"

# endregion

# Rank
# region


class Howrare(bases.Page):
    def __init__(self, collection_id: str) -> None:
        super().__init__(collection_id, url='https://howrare.is', id='Howrare')
        self.collection = collection_id

    def export(self, nft_id: str or int, **kwargs) -> int:
        "Export rank of nft with id, `None` mostly if not supported"
        if not self.valid:
            return None

        response = requests.get(f'{self.url}/{nft_id}')

        if response.status_code != 200:
            return None

        html = response.text
        data = BeautifulSoup(html, 'html.parser')
        rank = data.find('ul', {'class': 'attributes'}
                         ).contents[1].contents[3].getText()

        return int(rank)


class Moonrank(bases.Page):
    def __init__(self, collection_id: str) -> None:
        super().__init__(collection_id, url='https://moonrank.app/collection', id='Moonrank')
        self.collection = collection_id

    def export(self, nft_token: str or int, **kwargs) -> int:
        "Export rank of nft with id, `None` mostly if not supported"
        if not self.valid:
            return None

        response = requests.get(f'{self.url}/{nft_token}')

        if response.status_code != 200:
            return None

        html = response.text
        data = BeautifulSoup(html, 'html.parser')
        rank = data.find('span', {'x-text': 'rank'}).getText()

        return int(rank)

    def get_nft_url(self, nft_token: str or int) -> str:
        # TODO: implement this with Page base
        return f'{self.url}/{nft_token}'

# endregion

# endregion

# BUG: filter params before checking and waiting price
class MagicCollection(bases.Collection):
    def __init__(self, collection_id: str) -> None:
        "collection_id means collection name on marketplace"
        resposne = requests.get(
            f'https://api-mainnet.magiceden.io/rpc/getCollectionEscrowStats/{collection_id}'
        )

        if resposne.status_code != 200:
            raise Exception(f'Could not request {collection_id}')

        data = resposne.json()["results"]
        name = data['symbol'].replace('_', '').lower()

        collection_tuple = bases.PageTuple([Magiceden], collection_id)
        rank_tuple = bases.PageTuple([
            Howrare,
            Moonrank
        ], name)
        rarity_tuple = bases.PageTuple([], '')

        self.name = name
        super().__init__(f'https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q=%7B%22%24match%22%3A%7B%22collectionSymbol%22%3A%22{collection_id}%22%7D%2C%22%24sort%22%3A%7B%22createdAt%22%3A-1%7D%2C%22%24skip%22%3A0%2C%22%24limit%22%3A20%7D',
                         collection_id, collection_tuple, rank_tuple, rarity_tuple)

    def parse_nft(self, raw_nft: dict) -> bases.NFT:
        nft_name = raw_nft['title']
        nft_token = raw_nft['mintAddress']
        _, nft_id = nft_name.split('#')
        
        # price checking
        if not raw_nft['price']:
            time.sleep(4)
            raw_nft = get_nft(self.id, raw_nft['mintAddress'])

            if not raw_nft:
                return None

        # rank getting
        rank = self.rank_tuple.export(nft_id=nft_id, nft_token=nft_token)
        
        
        nft = bases.NFT(nft_id, nft_name, nft_token,
                        raw_nft['price'], raw_nft['img'], rank, {pair["trait_type"]: pair["value"] for pair in raw_nft['attributes']})

        return nft


def get_nft(collection_id: str, nft_token: str or int) -> dict:
    raw_nfts = get_nfts(collection_id)
    
    for raw_nft in raw_nfts:
        if raw_nft['mintAddress'] == nft_token:
            return raw_nft

    return None


def get_nfts(collection_id: str) -> List[dict]:
    "Get raw data nfts"
    url = f'https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q=%7B%22%24match%22%3A%7B%22collectionSymbol%22%3A%22{collection_id}%22%7D%2C%22%24sort%22%3A%7B%22createdAt%22%3A-1%7D%2C%22%24skip%22%3A0%2C%22%24limit%22%3A20%7D'

    response = requests.get(url)

    if response.status_code != 200:
        if response.status_code == 404:
            return None
        # BUG: here is infinite recursion
        time.sleep(5)
        return get_nfts(collection_id)

    nfts = response.json()

    return nfts["results"]


def parse_snapshot(snapshot: bases.Snapshot, collection: MagicCollection) -> List[bases.NFT]:
    "Create nft object list from raw nft snapshot"
    nfts = []

    for raw_nft in snapshot.list:
        nft = collection.parse_nft(raw_nft)
        if nft:
            nfts.append(nft)

    return nfts


def filter_snapshot(snapshot: bases.Snapshot or List[bases.NFT], **filters) -> List[bases.NFT]:
    "Filter snapshot"
    filtered = []

    att_treshold = 20 if 'treshold' not in filters.keys() else filters.pop('treshold')

    list_ = snapshot if type(snapshot) is list else snapshot.list

    for nft in list_:
        if not filters:
            continue

        # att filtering
        att_keys = list(filter(lambda key: key != 'price' and key != 'rank', filters.keys()))

        if att_keys:
            item_atts = nft.atts
            max_price = 0

            for att_key in att_keys:
                if att_key in item_atts.keys():
                    item_att_type =  item_atts[att_key]
                    if item_att_type in filters[att_key].keys():
                        att_floor = filters[att_key][item_att_type]
                        
                        max_price = max(float(att_floor), max_price)
            
            if not max_price:
                continue
            
            tresholded_max_price = max_price * (100 - att_treshold) / 100

            # TODO: workout this condition
            if nft.price <= tresholded_max_price:
                filtered.append(nft)
                continue

        else:
            # normal filterring
            if 'price' in filters.keys() and nft.price > float(filters['price']):
                continue
            
            if nft.rank is None:
                continue

            if 'rank' in filters.keys() and nft.rank > int(filters['rank']):
                continue

            filtered.append(nft)

    return filtered
