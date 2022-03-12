# import solanart
import meden
from crossplatform import core, core_types
from crossplatform import core_exceptions as errors

from typing import List, Dict


class FilterData:
    def __init__(self, **kwargs):
        result = {}

        for key, value in kwargs.items():
            if key in core_types.NFTFilters.__dict__.keys():
                filter_dict = core_types.NFTFilters.__dict__[key].value
                result[filter_dict["id"]] = lambda nftValue: filter_dict["func"](value, nftValue)
                 # id of the attribute in NFT class 
                 # function for checking the value

        self.data = result # dict of "nft_att": "filter_func"(value)


class CollectionData:
    def __init__(self, collectionID: str, rankID: str, filters: FilterData):
        self.id = collectionID
        self.rankID = rankID
        self.filterData = filters

        self.lastSnapshot = core.Snapshot([], [])

    def filter_snapshot(self, snapshot: core.Snapshot) -> core.Snapshot:
        result = []
        
        for nft in snapshot.list:
            valid = True
            
            for att, filter_func in self.filterData.data.items():
                valid = valid and filter_func(nft.__dict__[att])
                
                if not valid:
                    break

            if valid:
                result.append(nft)
            
        return core.Snapshot(result)

    def update_snapshot(self, newSnapshot: core.Snapshot) -> core.Snapshot:
        self.lastSnapshot = self.filter_snapshot(newSnapshot)
        return self.lastSnapshot


class Monitor:
    def __init__(self, marketPage: core.MarketPage) -> None:
        self.collections = {} # collectionID: CollectionData
        self.marketPage = marketPage

    def update(self) -> Dict[str, core.Snapshot]:
        if self.collections == {}:
            raise errors.General(f"There are no collections in {self} monitor")

        result = {}

        for collection in self.collections.values():
            snapshot = self.marketPage.get_snapshot(collection.id, collection.rankID)
            snapshot = collection.update_snapshot(snapshot)

            if snapshot.isEmpty():
                continue

            result[collection.id] = snapshot

        return result

    def add_collection(self, collectionID: str, rankID: str, **filters) -> None:
        if not self.marketPage._check_collection(collectionID):
            raise errors.NotValidQuerry(f"CollectionID {collectionID}")

        if collectionID in self.collections.keys():
            raise errors.General(f"Collection {collectionID} is already in monitor")

        self.collections[collectionID] = CollectionData(collectionID, rankID, FilterData(**filters))

    def remove_collection(self, collectionID: str):
        if not collectionID in self.collections:
            raise errors.NotValidQuerry(f"CollectionID {collectionID}")
        
        self.collections.pop(collectionID)

