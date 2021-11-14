import os
import time
import json
import enum
import uuid
from bs4 import BeautifulSoup

import requests



class DataLoader:
    @staticmethod
    def Save(data:object, path:str) -> None:
        "Save your object to file"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data.__dict__, f, ensure_ascii=False, indent=4)

    
    @staticmethod
    def Load(path:str, out_obj:object) -> object:
        """
        Load object form file
        \t returns None if action was unsuccessful 
        """
        if not os.path.exists(path):
            return None

        with open(path, 'r', encoding='utf-8') as f:
            return out_obj.__dict__.update(json.load(f))



class SolanartSnapshot:
    def __init__(self, data:list[dict], ids:list[int]=None) -> None:
        self.list = data
        
        if not ids:
            ids = [nft['id'] for nft in data]
        self.ids = ids


    def __sub__(self, other:"SolanartSnapshot") -> "SolanartSnapshot":
        "Get the difference between two lists, returns Snapshot object"
        final_ids = list(filter(lambda id: not id in other.ids, self.ids))
        final_list = [self.list[self.ids.index(id)] for id in final_ids]

        return SolanartSnapshot(final_list, final_ids)



class NFT:
    def __init__(self, id: str, name: str, token:str, price: float, image: str, rank:int, attributes: str) -> None:
        "NFT class for unifying nft objects"
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



class Collection:
    # TODO: rarity table
    # Page functions
    #region

    class Page:
        def __init__(self, url, collection) -> None:
            self.url = f'{url}/{collection}'
            self.support = self.get_support()
            self.id = 'None'


        def get_support(self) -> bool: 
            "Check if collection / given url exists"
            try: 
                response = requests.get(f'{self.url}')
                return response.status_code == 200
            except:
                return False


        def export_value(self, id):
            return None



    class Howrare(Page):
        def __init__(self, collection) -> None:
            super().__init__('https://howrare.is', collection)
            self.collection = collection
            self.id = 'Howrare'
            
            self.map = self._get_name_id_map()


        def _get_name_id_map(self):
            response = requests.get(f'{self.url}')
            data = BeautifulSoup(response.text, 'html.parser')

            # retruns how many aviable pages on howrare are there
            page_len = len(data.find_all('li', {'class': 'page-item'})) / 2
            page_len = int(page_len)
            result_map = {}

            for page_id in range(page_len):
                page_response = response = requests.get(f'{self.url}/?page={page_id}&sort_by=price')
                page_data = BeautifulSoup(page_response.text, 'html.parser')
                
                nft_id_elements = page_data.find_all('a', {'class':'m-2'})
                for nft_id_element in nft_id_elements:
                    id = nft_id_element['href']
                    id = id.replace(self.collection, '').replace('/', '')
                    id = int(id)

                    name = nft_id_element.find('h3').getText()
                    name = name.replace(' ', '').lower()
                    result_map[name] = id

                print(page_id)
            
            return result_map


        def export_value(self, nft) -> int:
            if not self.support:
                return None

            name = nft['name'].replace(' ', '').lower()
            
            if not name in self.map.keys():
                # TODO
                return 9999
            
            id = self.map[name]
            response = requests.get(f'{self.url}/{id}')

            if not response.status_code == 200:
                return None

            html = response.text
            data = BeautifulSoup(html, 'html.parser')
            rank = data.find('ul', {'class': 'attributes'}).contents[1].contents[3].getText()

            return int(rank)

    

    class Moonrank(Page):
        def __init__(self, collection) -> None:
            super().__init__('https://moonrank.app/collection', collection)
            self.id = 'Moonrank'


        def export_value(self, nft_id) -> int:
            if not self.support:
                return None

            response = requests.get(f'{self.url}/{nft_id}')

            if not response.status_code == 200:
                return None

            html = response.text
            data = BeautifulSoup(html, 'html.parser')
            rank = data.find("span", attrs={'x-text': 'rank'}).getText()

            return int(rank)

    #endregion

    def __init__(self, collection:str) -> None:
        data = requests.get('https://qzlsklfacc.medianetwork.cloud/get_collection_url?url=cyberpharmacist').json()[0]
        
        self.collection = collection
        self.name = data['name'].replace(' ', '').lower()
        self.rank_pages = (
            Collection.Howrare(self.name),
            Collection.Moonrank(self.name)
        )

        self.rank_support = self._get_rank_support()
        self.rarity_table = None


    def parse_nft(self, raw_nft) -> NFT:
        "Export nft dict to proper nft object "
        rank = self._get_rank(raw_nft)
        nft = NFT(raw_nft['id'], raw_nft['name'], raw_nft['token_add'], raw_nft['price'], raw_nft['link_img'], rank, raw_nft['attributes'])

        return nft

    
    # private
    def _get_rank_support(self) -> Page:
        "Check if any of request pages support this collection, if yes return the page"
        support = None

        for i, page in enumerate(self.rank_pages):
            if page.support:
                support = i
                break
                
        return support


    def _get_rank(self, nft_id) -> int:
        "Get rank of nft from supported page, returns None if ranks aren't supported"
        if self.rank_support is None:
            return None

        return self.rank_pages[self.rank_support].export_value(nft_id)


    def _get_rarity_table(self) -> dict:
        # TODO
        pass


def get_nfts(collection:Collection) -> list[dict]:
    url = f'https://qzlsklfacc.medianetwork.cloud/nft_for_sale?collection={collection.collection}'
    nfts = requests.get(url).json()
    
    return nfts


def parse_snapshot(snapshot:SolanartSnapshot, collection:Collection) -> list[NFT]:
    nfts = []

    for raw_nft in snapshot.list:
        nft = collection.parse_nft(raw_nft)
        nfts.append(nft)

    return nfts


def filter_snapshot(snapshot:SolanartSnapshot or list[NFT], **filters) -> list[NFT]:
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


if __name__ == "__main__":
    collection = Collection('cyberpharmacist')
    old_nfts = get_nfts(collection)
    old_snap = SolanartSnapshot(old_nfts)
    print('old_snap_done')

    old_snap.list.pop(0)
    old_snap.ids.pop(0)

    #time.sleep(10)

    new_nfts = get_nfts(collection)
    new_snap = SolanartSnapshot(new_nfts)
    print('new_snap_done')   

    result = new_snap - old_snap 
    parsed_result = parse_snapshot(result, collection)
    print('X')
