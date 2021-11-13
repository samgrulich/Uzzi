import os
import math
import enum
import requests

from matplotlib import pyplot as plt
from bs4 import BeautifulSoup

# from code import PROJECT_PATH
# from code.new_db import Data, Database
from db import DataSet, Database



class Attribute:
    def __init__(self, type_:str) -> None:
        "Keep track of atribute data"
        self.type = type_
        self.values = {}

    
    def Add(self, value: str, rarity: str or float) -> None:
        "Add rarity"
        self.values[value] = float(rarity)


    def Rarity(self, value: str) -> float:
        "Get rarity of one value"
        if value == 'None':
            return 0.0
        return self.values[value]



class NFT:
    def __init__(self, id: str, name: str, token:str, price: float, rank: int, image: str, attributes: dict) -> None:
        "NFT class for unifying nft objects"
        self.id = id
        self.name = name
        self.price = price
        self.rank = rank
        self.img = image
        self.token = token
        self.atts = attributes

    # public
    def vars(self) -> dict:
        "Get dictionary of variables"
        return vars(self)



class Parser:
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


    def __init__(self, collection, *pages) -> None:
        self.pages = [page for page in pages]
        self.support = self.get_support()


    def get_support(self) -> int:
        """
        Check all of the pages for support, \n
        \t returns index of supported page
        """
        support = None

        for i, page in enumerate(self.pages):
            support = page.get_support()

            if support:
                support = i

        return support


    def export_value(self, id) -> int:
        "Get rank value from supported page"
        if not self.support:
            return None

        page = self.pages[self.support]
        return page.export_value(id)
    

    @property
    def supported_page(self) -> Page:
        "Return supported page if none is, returns None"
        if self.support is None:
            return None
            
        return self.pages[self.support]

    

class RankParser(Parser):
    # Page functions
    #region

    class Howrare(Parser.Page):
        def __init__(self, collection) -> None:
            self.id = 'Howrare'
            super().__init__('https://howrare.is', collection)


        def export_value(self, nft_id) -> int:
            if not self.support:
                return None

            response = requests.get(f'{self.url}/{nft_id}')

            if not response.status_code == 200:
                return None

            html = response.text
            data = BeautifulSoup(html, 'html.parser')
            rank = data.find("span", string="Rank").find_next('span').contents[0].getText()

            return int(rank)

    

    class Moonrank(Parser.Page):
        def __init__(self, collection) -> None:
            self.id = 'Moonrank'
            super().__init__('https://moonrank.app/collection', collection)


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

    def __init__(self, collection) -> None:
        super().__init__(collection, 
            RankParser.Howrare(collection),
            RankParser.Moonrank(collection))


    def export_rank(self, nft_id) -> int:
        "Get rank value from supported page"
        return super().export_value(nft_id)



class NFTParser(Parser):
    # Page functions
    #region

    class Solanart(Parser.Page):
        def __init__(self, collection) -> None:
            url = 'https://qzlsklfacc.medianetwork.cloud'
            self.id = 'Solanart'

            self.url = f'{url}/nft_for_sale?collection={collection}'
            self.rarity_url = f'{url}/rarity?collection={collection}'
            self.support = self.get_support()
            self.atts = self._parse_atts()
            self.rank_parser = RankParser(collection)


        def export_nft(self, nft_raw) -> NFT:
            "Export raw nft dict to polished NFT object"
            nft_atts = self._parse_nft_atts(nft_raw['attributes'])
            
            nft = NFT(nft_raw['id'], nft_raw['name'], nft_raw['token_add'], nft_raw['price'], self.rank_parser.export_value(nft_raw['id']), nft_raw['link_img'], nft_atts)

            return nft


        def export_nfts(self) -> list[NFT]:
            "Export all nfts in raw data to list of polished nft objects"
            nfts_raw = requests.get(self.url).json()
            nfts = []

            for nft_raw in nfts_raw:
                nft = self.export_nft(nft_raw)
                nfts.append(nft)

            return nfts
        

        # private
        #region
        
        def _parse_atts(self) -> dict:
            "Extract rarities from rawdata to att_type:att_value:att_rarity table"
            rawdata = requests.get(self.rarity_url).json()
            atts = {}

            for key, rarity in rawdata.items():
                att_type, att_value = key.split(':')
                att_rarity = float(rarity)

                if not att_type in atts.keys():
                    atts[att_type] = Attribute(att_type)
                
                att_value = att_value.replace(' ', '')
                atts[att_type].Add(att_value, att_rarity)

            return atts


        def _parse_nft_atts(self, atts_str:str) -> dict:
            "Extract attributes from raw data and add meta data to them"
            atts = atts_str.split(',')
            parsed_atts = {}
            att_rarities = self.atts

            for att in atts:
                type_, data_ = att.replace(' ', '').split(':')

                value_ = float(att_rarities[type_].Rarity(data_))
                parsed_atts[type_] = {data_: value_}

            parsed_atts['atributeCount'] = len(parsed_atts)
            return parsed_atts

        #endregion


    class Magiceden(Parser.Page):
        def __init__(self, collection) -> None:
            self.id = 'Magiceden'
            super().__init__('https://magiceden.io/marketplace', collection)


        def export_nfts(self) -> list[NFT]:
            pass

    #endregion

    
    def __init__(self, collection) -> None:
        super().__init__(collection, 
            NFTParser.Solanart(collection))


    def parse(self, nft: dict) -> NFT:
        if self.support == None:
            return None

        return self.pages[self.support].export_nft(nft)


    def parse_all(self) -> list[NFT]:
        if self.support == None:
            return None

        return self.pages[self.support].export_nfts()



def get_last_nft(collection, nft_parser) -> NFT:
    last_nft_raw = requests.get(f'https://qzlsklfacc.medianetwork.cloud/nft_for_sale?collection={collection}').json()[0]
    last_nft = nft_parser.parse(last_nft_raw)

    return last_nft


def turbo_check(collection, database, nft_parser) -> bool:
    """
    Check if last nft is the sasme as last in database
    \t return True if it has changed
    """
    last_nft = get_last_nft(collection, nft_parser)
    
    return not database.id_cache[0] == last_nft.id



if __name__ == '__main__':
    database = Database(0, './DBs/').Load()
    nft_parser = NFTParser('cyberpharmacist')

    condition = turbo_check('cyberpharmacist', database, nft_parser)
    
    if not condition:
        # database update
        nfts = nft_parser.parse_all()
        nfts.reverse()

        for nft in nfts:
            database.Add(nft.vars())

        database.Save()

        # update request
        database.Request()
