import requests
import time
from bs4 import BeautifulSoup
from united import bases


# Pages
# region

#  Collection
# region

class Solanart(bases.Page):
    def __init__(self, collection: str) -> None:
        super().__init__(collection, 'https://solanart.io/collections', id='Solanart')

# endregion


#  Ranking
# region

class RankTuple(bases.PageTuple):
    def export(self, nft_id: str or int, nft_name: str) -> int:
        return super().export(id=nft_name)


class Howrare(bases.Page):
    def __init__(self, collection: str) -> None:
        super().__init__(collection, url='https://howrare.is', id='Howrare')
        self.collection = collection

        self.map = self._get_name_id_map()

    def _get_name_id_map(self) -> dict:
        # TODO: optimize this
        response = requests.get(f'{self.url}')
        data = BeautifulSoup(response.text, 'html.parser')

        # retruns how many aviable pages on howrare are there
        page_len = len(data.find_all('li', {'class': 'page-item'})) / 2
        page_len = int(page_len)
        result_map = {}

        for page_id in range(page_len):
            page_response = requests.get(
                f'{self.url}/?page={page_id}&sort_by=price')
            page_data = BeautifulSoup(page_response.text, 'html.parser')

            nft_id_elements = page_data.find_all('a', {'class': 'm-2'})
            for nft_id_element in nft_id_elements:
                id = nft_id_element['href']
                id = id.replace(self.collection, '').replace('/', '')
                id = int(id)

                name = nft_id_element.find('h3').getText()
                name = name.replace(' ', '')
                result_map[name] = id

            print(page_id)

        return result_map
    
    def export(self, id: str or int) -> int:
        "Export rank of nft with id, `None` mostly if not supported"
        if not self.valid:
            return None

        name = id.replace(' ', '')

        if not name in self.map.keys():
            # TODO: check other pages
            return None

        id = self.map[name]
        response = requests.get(f'{self.url}/{id}')

        if response.status_code != 200:
            return None

        html = response.text
        data = BeautifulSoup(html, 'html.parser')
        rank = data.find('ul', {'class': 'attributes'}
                         ).contents[1].contents[3].getText()

        return int(rank)


class Moonrank(bases.Page):
    # TODO: you know body n stuff

    pass

# endregion

# endregion


class SolCollection(bases.Collection):
    def __init__(self, collection_id: str) -> None:
        "url is string before collection, collection means collection name"
        resposne = requests.get(
            f'https://qzlsklfacc.medianetwork.cloud/get_collection_url?url={collection_id}')

        if resposne.status_code != 200:
            raise Exception(f'Could not request {collection_id}')

        data = resposne.json()[0]
        name = data['name'].replace(' ', '').lower()

        collection_tuple = bases.PageTuple([Solanart], collection_id)
        rank_tuple = RankTuple([
            Howrare
        ], name)
        rarity_tuple = bases.PageTuple([], '')

        self.name = name
        super().__init__('https://qzlsklfacc.medianetwork.cloud/nft_for_sale?collection=',
                         collection_id, collection_tuple, rank_tuple, rarity_tuple)

    def parse_nft(self, raw_nft: dict) -> bases.NFT:
        rank = self.rank_tuple.export(raw_nft['id'], raw_nft['name'])
        nft = bases.NFT(raw_nft['id'], raw_nft['name'], raw_nft['token_add'],
                          raw_nft['price'], raw_nft['link_img'], rank, raw_nft['attributes'])

        return nft


def get_nfts(collection_id: str) -> list(dict):
    "Get raw data nfts"
    url = f'https://qzlsklfacc.medianetwork.cloud/nft_for_sale?collection={collection_id}'

    response = requests.get(url)

    if response.status_code != 200:
        if response.status_code == 404:
            return None
        # BUG: here is infinite recursion
        time.sleep(5)
        return get_nfts(collection_id)

    nfts = response.json()

    return nfts


def parse_snapshot(snapshot: bases.Snapshot, collection: SolCollection) -> list(bases.NFT):
    "Create nft object list from raw nft snapshot"
    nfts = []

    for raw_nft in snapshot.list:
        nft = collection.parse_nft(raw_nft)
        nfts.append(nft)

    return nfts


def filter_snapshot(snapshot: bases.Snapshot or list(bases.NFT), **filters) -> list(bases.NFT):
    "Filter snapshot"
    filtered = []

    list_ = snapshot if type(snapshot) is list else snapshot.list

    for nft in list_:
        if 'price' in filters.keys() and nft.price > float(filters['price']):
            continue

        if 'rank' in filters.keys() and nft.rank > int(filters['rank']):
            continue

        # attribute filtering
        # if filters:
        #     item_attributes = nft.attributes
        #     for att_type, att_rarity in filters.items():
        #         if att_type in item_attributes.keys() and next(iter(item_attributes.values())) < att_rarity:
        #             condition = False
        #             continue

        filtered.append(nft)

    return filtered
