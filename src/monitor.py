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
                result[filter_dict["id"]] = lambda nft_value: filter_dict["func"](value, nft_value)
                 # id of the attribute in NFT class 
                 # function for checking the value

        self.data = result # dict of "nft_att": "filter_func"(value)


class CollectionData:
    def __init__(self, collectionId: str, rankId, filters: FilterData):
        self.id = collectionId
        self.rankId = rankId
        self.filterData = filters

        self.lastSnapshot = None

    def filter_snapshot(self, snapshot: core.Snapshot) -> core.Snapshot:
        result = []
        
        for nft in snapshot.list:
            valid = True
            
            for att, filter_func in self.filterData.data.items():
                valid &= filter_func(nft.__dict__[att])
                
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
        self.collections = []
        self.collectionIds = {}
        self.marketPage = marketPage

    def update(self) -> Dict[str, core.Snapshot]:
        if self.collections == []:
            raise errors.General(f"There are no collections in {self} monitor")

        result = {}

        for collection in self.collections:
            snapshot = self.marketPage.get_snapshot(collection.id, collection.rankId)
            snapshot = collection.update_snapshot(snapshot)

            if snapshot.isEmpty():
                continue

            result[collection.id] = snapshot

        return result

    def add_collection(self, collectionId: str, rankId: str, **filters) -> None:
        if not self.marketPage._check_collection(collectionId):
            raise errors.NotValidQuerry(f"CollectionID {collectionId}")

        self.collectionIds[collectionId] = len(self.collections)
        self.collections.append(CollectionData(collectionId, rankId, FilterData(**filters)))

    def remove_collection(self, collectionId: str):
        if not collectionId in self.collectionIds:
            raise errors.NotValidQuerry(f"CollectionID {collectionId}")

        collectionId, index = self.collectionIds.pop(collectionId)
        self.collections.pop(index)


# magiceden = meden.Magiceden()

# monitor = Monitor(magiceden)
# monitor.add_collection('blockparty', price=2, rank=600)

# monitor.update()
