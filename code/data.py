import os
import math
import enum
import requests

from matplotlib import pyplot as plt
from bs4 import BeautifulSoup

# from code import PROJECT_PATH
# from code.new_db import Data, Database
from db import Data, Database



class Querry:
    class Type(enum.Enum):
        rarity = 'rarity?collection='
        nfts = 'nft_for_sale?collection='
        general = 'query_volume_per_collection?collection='
    


    URL = 'https://qzlsklfacc.medianetwork.cloud/'


    def __init__(self, querry: Type, collection: str) -> None:
        """
        Store important querry data 
        """
        self.querry = querry
        self.collection = collection


    def Get_rawdata(self, collection:str=None) -> dict:
        """
        Request data from internet 
        \t returns dictionary
        """
        if not collection:
            collection = self.collection
        
        return requests.get(self.url).json()


    @property
    def url(self) -> str:
        return f'{Querry.URL}{self.querry.value}{self.collection}'



class Attribute():
    def __init__(self, type_:str) -> None:
        "Keep track of atribute data"
        self.type = type_
        self.values = {}

    
    def Add(self, value: str, rarity: str or float) -> None:
        "Add rarity"
        self.values[value] = float(rarity)


    def Rarity(self, value: str) -> float:
        "Get rarity of one value"
        return self.values[value]

    
    @property
    def sum(self) -> float:
        "Sum of rarities "
        return sum(self.values.values())



class CollectionData(Querry):
    def __init__(self, collection: str) -> None:
        super().__init__(Querry.Type.rarity, collection)
    

    # private:
    def _parse_attribs_rarities(self) -> dict:
        """
        Export attribs from json data object \n
         returns dict obj
        """
        rawdata = self.Get_rawdata()
        attribs = {}

        for key in rawdata.keys():
            att_type, att_value = key.split(':')
            att_rarity = float(rawdata[key])

            if not att_type in attribs.keys():
                attribs[att_type] = Attribute(att_type)
            
            att_value = att_value.replace(' ', '')
            attribs[att_type].Add(att_value, att_rarity)

        for attrib in attribs.values():
            if not math.ceil(attrib.sum) == 100:
                attribs[att_type].Add('None', 100 - attrib.sum)

        return attribs


    @property
    def attribs(self):
        "Actually attribs are being updated every call, so I strongly `recommend to keep copy of them`"
        return self._parse_attribs_rarities()



class RankParser:
    # Page functions
    #region

    class Page:
        def __init__(self, url, collection) -> None:
            self.url = f'{url}/{collection}'
            self.support = self.get_support()
        

        def get_support(self, nft_id='') -> bool:
            "Check wheter this page is on web"
            response = requests.get(f'{self.url}/{nft_id}')
            return response.status_code == 200


        def export_rank(self, nft_id) -> int:
            "Extract rank of nft"
            return None



    class Howrare(Page):
        def __init__(self, collection) -> None:
            super().__init__('https://howrare.is', collection)


        def export_rank(self, nft_id) -> int:
            if not self.support:
                return None

            response = requests.get(f'{self.url}/{nft_id}')

            if not response.status_code == 200:
                return None

            html = response.text
            data = BeautifulSoup(html, 'html.parser')
            rank = data.find("span", string="Rank").find_next('span').contents[0].getText()

            return int(rank)

    

    class Moonrank(Page):
        def __init__(self, collection) -> None:
            super().__init__('https://moonrank.app/collection', collection)


        def export_rank(self, nft_id) -> int:
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
        self.pages = [
            RankParser.Howrare(collection),
            RankParser.Moonrank(collection)
        ]

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


    def export_rank(self, nft_id) -> int:
        "Get rank value from supported page"
        if not self.support:
            return None

        page = self.pages[self.support]
        return page.export_rank(nft_id)



class NFTData(Querry):
    def __init__(self, collection: str) -> None:
        super().__init__(Querry.Type.nfts, collection)

        self.nfts = None
        self.rank_parser = RankParser(collection)
        self.rarities = CollectionData(collection)


    def Extract_nft(self, nft: dict, attrib_rarities: dict, rank_support:bool=False) -> dict:
        """
        Extract atributes, rank for easier manipulation with each nft
        \t returns nft
        """
        attribs = nft['attributes'].split(',')
        parsed_attribs = {}
        attribs_sum = 10


        # parse attrib rarities
        for attrib in attribs:
            type_, data_ = attrib.replace(' ', '').split(':')

            if data_ == 'None':
                attribs_sum -= 1

                continue

            value_ = float(attrib_rarities[type_].Rarity(data_))
            parsed_attribs[type_] = {data_: value_}

        parsed_attribs['AttributeCount'] = attribs_sum


        # parse rank
        rank = self.rank_parser.export_rank(nft['id'])


        # save data
        nft['attributes'] = parsed_attribs
        nft['rank'] = rank
        return nft


    def Extract_nfts(self) -> list[dict]:
        """
        Download and extract nfts for easier code manipulation
        \t returns list of nfts
        """
        self.rarities = CollectionData(self.collection)
        rawdata = self.Get_rawdata(self.collection)
        data = []
        rarities = self.rarities.attribs

        for i, nft in enumerate(rawdata):
            nft_data = self.Extract_nft(nft, rarities)
            data.append(nft_data)

        data.reverse()

        self.nfts = data
        return data



def load_nfts(collection) -> list[dict]:
    raw_nfts = NFTData(collection)
    nfts = raw_nfts.Extract_nfts()
    return nfts


if __name__ == '__main__':
    nfts = load_nfts('cyberpharmacist')
    database = Database(0, './DBs/')

    for nft in nfts:
        database.Add(nft)

    database.Save()
