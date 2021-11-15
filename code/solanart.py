import requests
import time
from bs4 import BeautifulSoup
from united import objects


# Pages
# region

#  Collection
# region

class Solanart(objects.Page):
    def __init__(self, collection: str) -> None:
        super().__init__(collection, 'https://solanart.io/collections', id='Solanart')

# endregion


#  Ranking
# region

class RankTuple(objects.PageTuple):
    def export(self, nft_id: str or int, nft_name: str) -> int:
        return super().export(nft_id, nft_name)


class Howrare(objects.Page):
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

    def export(self, nft_id: str or int, nft_name: str) -> int:
        "Export rank of nft with id, `None` mostly if not supported"
        if not self.valid:
            return None

        name = nft_name.replace(' ', '')

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


class Moonrank(objects.Page):
    # TODO: you know body n stuff

    pass

# endregion

# endregion


class SolCollection(objects.Collection):
    def __init__(self, url: str, collection: str) -> None:
        "url is string before collection, collection means collection name"
        resposne = requests.get(
            f'https://qzlsklfacc.medianetwork.cloud/get_collection_url?url={collection}')

        if resposne.status_code != 200:
            raise Exception(f'Could not request {collection}')

        data = resposne.json()[0]
        name = data['name'].replace(' ', '').lower()

        collection_tuple = objects.PageTuple([Solanart], collection)
        rank_tuple = RankTuple([
            Howrare
        ], name)
        rarity_tuple = objects.PageTuple(None, None)

        super().__init__(url, name, collection_tuple, rank_tuple, rarity_tuple)

    def parse_nft(self, raw_nft: dict) -> objects.NFT:
        rank = self.rank_tuple.export(raw_nft['id'], raw_nft['name'])
        nft = objects.NFT(raw_nft['id'], raw_nft['name'], raw_nft['token_add'],
                          raw_nft['price'], raw_nft['link_img'], rank, raw_nft['attributes'])

        return nft


def get_nfts(collection_id:str) -> list[dict]:
    "Get raw data nfts"
    url = f'https://qzlsklfacc.medianetwork.cloud/nft_for_sale?collection={collection_id}'
    
    response = requests.get(url)

    if response.status_code != 200:
        time.sleep(5)
        return get_nfts(collection_id)

    nfts = requests.get(url).json()
    
    return nfts

def parse_snapshot(snapshot:objects.Snapshot, collection:SolCollection) -> list[objects.NFT]:
    "Create nft object list from raw nft snapshot"
    nfts = []

    for raw_nft in snapshot.list:
        nft = collection.parse_nft(raw_nft)
        nfts.append(nft)

    return nfts

def filter_snapshot(snapshot:objects.Snapshot or list[objects.NFT], **filters) -> list[objects.NFT]:
    "Filter snapshot"
    filtered = []

    list_ = snapshot if type(snapshot) is list else snapshot.list

    for nft in list_:
        condition = True

        if 'price' in filters.keys() and nft.price > float(filters['price']):
            condition = False
            continue

        if 'rank' in filters.keys() and nft.rank > int(filters['rank']):
            condition = False
            continue
        
        # attribute filtering
        # if filters:
        #     item_attributes = nft.attributes
        #     for att_type, att_rarity in filters.items():
        #         if att_type in item_attributes.keys() and next(iter(item_attributes.values())) < att_rarity:
        #             condition = False
        #             continue

        if condition:
            filtered.append(nft)

    return filtered
