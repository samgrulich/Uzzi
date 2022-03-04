# import solanart
import meden
from crossplatform import core, exceptions, types

from typing import List, Tuple, Dict


class FilterData:
    def __init__(self, **kwargs):
        result = {}

        for key, value in kwargs.items():
            if key in types.NFTFilters.__dict__.keys():
                filter_dict = types.NFTFilters.__dict__[key]
                result += {
                    filter_dict["id"]: # id of the attribute in NFT class
                    lambda nft_value: filter_dict["func"](value, nft_value) # function for checking the value
                }

        self.data = result # dict of "nft_att": "filter_func"(value)


class CollectionData:
    def __init__(self, collectionId: str, filters: FilterData):
        self.id = collectionId
        self.filterData = filters

        self.lastSnapshot = None

    def filter_snapshot(self, snapshot: core.Snapshot) -> core.Snapshot:
        result = []
        
        for nft in snapshot.list:
            valid = True
            
            for att, filter_func in self.filterData.data.items():
                valid &= filter_func(nft[att])
                
                if not valid:
                    break

            if valid:
                result += nft
            
        return core.Snapshot(result)

    def update_snapshot(self, newSnapshot: core.Snapshot) -> core.Snapshot:
        self.lastSnapshot = self.filter_snapshot(newSnapshot)

        return self.lastSnapshot


class Monitor:
    def __init__(self, marketPage: core.MarketPage) -> None:
        self.collections = None
        self.marketPage = marketPage


    def update(self) -> Dict[str, core.Snapshot]:
        if self.collections == None:
            raise exceptions.General(f"There are no collections in {self} monitor")

        result = {}

        for collection in self.collections:
            snapshot = core.MarketPage.get_snapshot(collection.id)
            collection.update_snapshot(snapshot)

            result += {collection["id"]: snapshot}

        return result

    # def set_filters(self, **filters) -> None:
    #     "Cahnge nft filters"
    #     self.filters = filters


# monitor = Monitor('cyberpharmacist', Background=10)
