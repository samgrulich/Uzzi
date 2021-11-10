import time

from code.database import DataBase
from code.data import NFTData, Comparator



class Monitor:
    def __init__(self, collection:str, database:DataBase=DataBase(), **kwargs) -> None:
        keys = kwargs.keys()

        time_now = 5e12 #5e9 # - 5sec
        e_type = [0, 1]
        price = 100

        if 'time' in keys:
            time = kwargs.pop('time')
        
        if 'e_type' in keys:
            e_type = kwargs.pop('e_type')

        if 'price' in keys:
            price = kwargs.pop('price')
        
        self.filters = kwargs
        self.time = time_now
        self.e_type = e_type
        self.price = price
        self.database = database
        self.collection = collection
        self.log = database.log.data


    def update(self, filter=True) -> dict:
        data = NFTData(self.collection)
        nfts = data.parse_rarities()

        Comparator(self.database, nfts, 'add_new')
        self.database.save()

        if filter:
            result = self.filter()
            return result
        return None


    def filter(self) -> dict:
        time_now = time.time_ns()
        min_time = time_now - int(self.time)

        index = -1
        for i, log_time in enumerate(self.log.keys()):
            if int(log_time) <= min_time:
                index = i - 1
                break

        if index == -1:
            print('index -1')
            return None

        log_values = list(self.log.values())[:index+1]
        indicies = []
        for slice_i, log_slice in enumerate(log_values):
            for nft_i, nft in enumerate(log_slice):
                if nft['e_type'] == 0 or 1:
                    if nft['data']['price'] <= self.price:
                        indicies.append([slice_i, nft_i])

        if not len(indicies):
            print('not enough indicies')
            return None

        for index in indicies:
            attributes = log_values[index[0]][index[1]]['data']['attributes']
            attributes_keys = attributes.keys()

            result = True
            for filter_key, filter_val in self.filters.items():
                if filter_key in attributes_keys:
                    if not list(attributes[filter_key].values())[0] <= filter_val:
                        result = False
                        break

            if not result:
                indicies.remove(index)

        # recreate array from indicies
        log_keys = list(self.log.keys())[:index[0] + 1]
        result = {}
        for index in indicies:
            #index = index - 1
            key = log_keys[index[0]]

            if not key in result.keys():
                result[key] = []
            result[key].append(log_values[index[0]][index[1]])

        return result

monitor = Monitor('cyberpharmacist', Background=10)
result = monitor.filter()

# print(result)
        
