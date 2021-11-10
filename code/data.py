import os
import math
import enum
import requests

from matplotlib import pyplot as plt

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



class NFTData(Querry):
    def __init__(self, collection: str) -> None:
        super().__init__(Querry.Type.nfts, collection)

        self.nfts = None
        self.rarities = CollectionData(self.collection)


    def Extract_nft(self, nft: dict, attrib_rarities: dict) -> dict:
        """
        Extract atributes for easier manipulation with each nft
        \t returns nft
        """
        attribs = nft['attributes'].split(',')
        parsed_attribs = {}
        attribs_sum = 10

        for attrib in attribs:
            type_, data_ = attrib.replace(' ', '').split(':')

            if data_ == 'None':
                attribs_sum -= 1

                continue

            value_ = float(attrib_rarities[type_].Rarity(data_))
            parsed_attribs[type_] = {data_: value_}

        parsed_attribs['AttributeCount'] = attribs_sum
        nft['attributes'] = parsed_attribs
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
