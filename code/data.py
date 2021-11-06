import math
import enum
import requests

from matplotlib import pyplot as plt

from database import DataBase



class Querry(enum.Enum):
    rarity = 'rarity?collection='
    nfts = 'nft_for_sale?collection='
    general = 'query_volume_per_collection?collection='



class UrlData:
    URL = 'https://qzlsklfacc.medianetwork.cloud/'

    def __init__(self, querry: Querry, collection: str) -> None:
        self.url = f'{UrlData.URL}{querry.value}{collection}'
        self.querry = querry
        self.collection = collection



class Getter:
    def __init__(self, querry: Querry, collection: str) -> None:
        url_data = UrlData(querry, collection)
        self.url_data = url_data

        data = requests.get(url_data.url).json()
        self.data = data



class RarityGetter(Getter):
    def __init__(self, collection: str) -> None:
        super().__init__(Querry.rarity, collection)
    

    # public: 
    def plot_attribs(self, attrib_type, *flags) -> None:
        """
        Plots given attrib \n
        flags: \n
        \t showKeys - show attbibs type options
        \t silent - don't print attrib data
        """
        attribs = self.attribs
        attrib_pairs = attribs[attrib_type]

        if 'showKeys' in flags:
            print('keys: ', attribs.keys())
        
        if not 'silent' in flags:
            print('attrib_data', attrib_pairs)

        for label, value in attrib_pairs.items():
            plt.bar(label, float(value))

        plt.title(f'{self.url_data.collection} {attrib_type} rarity')
        plt.xticks(rotation = 45)

        plt.show()
    

    # private:
    def _get_attribs(self) -> dict:
        """
        Export attribs from json data object \n
         returns dict obj
        """
        data = self.data
        attribs = {}
        attribs_sum = {}

        for key in data.keys():
            type_, data_ = key.split(':')
            rarity_ = float(data[key])

            if not type_ in attribs.keys():
                attribs[type_] = {}
                attribs_sum[type_] = 0
            
            data_ = data_.replace(' ', '')
            attribs[type_][data_] = rarity_
            attribs_sum[type_] += rarity_
        
        for attrib_sum in attribs_sum.items():
            type_, value_ = attrib_sum
            
            if not math.ceil(value_) == 100:
                attribs[type_]['None'] = 100 - value_

        return attribs


    @property
    def attribs(self):
        return self._get_attribs()



class NFTGetter(Getter):
    def __init__(self, collection: str) -> None:
        super().__init__(Querry.nfts, collection)


    def parse_rarity(self, nft: dict, attrib_rarities: dict):
        attribs = nft['attributes'].split(',')
        parsed_attribs = {}
        attribs_sum = 10

        for attrib in attribs:
            type_, data_ = attrib.replace(' ', '').split(':')

            if data_ == 'None':
                attribs_sum -= 1

                continue

            value_ = float(attrib_rarities[type_][data_])
            parsed_attribs[type_] = {data_: value_}

        parsed_attribs['AttributeCount'] = attribs_sum
        nft['attributes'] = parsed_attribs
        return nft


    def parse_rarities(self):
        rarities = RarityGetter(self.url_data.collection)
        data = []

        for nft in self.data:
            nft_data = self.parse_rarity(nft, rarities.attribs)
            data.append(nft_data)

        return data



class GeneralGetter:
    """
    Not aviable yet
    """
    pass



class Comparator:
    def __init__(self, database: DataBase, data: list, *actions) -> None:
        self.database = database
        self.data = data
        
        for action in actions:
            if hasattr(self.__class__, action) and callable(getattr(self.__class__, action)):
                func = eval(f'self.{action}')
                func()


    def add_new(self):
        ids = self.database.data['ids']
        last_nft_index = -1

        for i, nft in enumerate(self.data):
            if nft['id'] == ids[0]:
                last_nft_index = i
                break
        
        print(f'updating {last_nft_index}')
        
        for nft in self.data[:last_nft_index]:
            self.database.add(nft)

    
    def update(self):
        """
        Prefer using add_new instead
        """
        for nft in self.data[:50]:
            self.database.add(nft)
            

# rarities = RarityGetter('cyberpharmacist')
# # print(rarities.attribs)
# rarities.plot_attribs('Brain', 'showKeys')

# data = NFTGetter('cyberpharmacist')
# attribs = data.parse_rarity(data.data[1], rarities.attribs)
# print(attribs)
# data = NFTGetter('cyberpharmacist')
# nfts = data.parse_rarities()

# db = DataBase()
# comparator = Comparator(db, nfts, 'add_new')
# db.save()