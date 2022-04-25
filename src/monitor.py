import asyncio
import collections
import meden
import time
from concurrent.futures import ThreadPoolExecutor
from crossplatform import core, core_types, network
from crossplatform import core_exceptions as errors

# debug imports
from typing import List, Dict, Tuple
from crossplatform.debug import debug_print



def parse_kwargs(args) -> dict:
    kwargs = {}

    for arg in args:
        string = str(arg)

        if '=' in string:
            key, value = string.split('=', 1)
            kwargs[key] = value

    return kwargs


class FilterData:
    def __init__(self, **kwargs):
        result = {}

        for key, value in kwargs.items():
            if key in core_types.NFTFilters.__dict__.keys():
                filter_dict = core_types.NFTFilters.__dict__[key].value
                result[filter_dict["id"]] = lambda nftValue, _value=value: (
                    filter_dict["func"])(_value, nftValue)
                # id of the attribute in NFT class
                # function for checking the value

        self.data = result  # dict of "nft_att": "filter_func"(value)


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
        self.collections = {}  # collectionID: CollectionData
        self.marketPage = marketPage

    async def update(self) -> Dict[str, core.Snapshot]:
        if self.collections == {}:
            raise errors.General(f"There are no collections in {self} monitor")

        startTime = time.time_ns()
        print("loop start ")

        with ThreadPoolExecutor(max_workers=100) as executor:
            thread1 = executor.map(self.update_collection, self.collections.values())

        rawSnaps = [result for result in list(thread1)]
        validSnaps = list(filter(lambda snapTuple: not snapTuple[1].isEmpty(), rawSnaps)) 
        result = {snapTuple[0]: snapTuple[1] for snapTuple in validSnaps}

        if len(result):
            debug_print(f"Update result len: {len(result)}", "Monitor")

        print("loop done", time.time_ns() - startTime)

        return result

    def update_collection(self, collection: CollectionData) -> Tuple[str, core.Snapshot]:
        snapshot = self.marketPage.get_snapshot(
            collection.id, collection.rankID)
        snapshot = collection.update_snapshot(snapshot)

        return (collection.id, snapshot)

    def add_collection(self, collectionID: str, rankID: str, **filters) -> None:
        if not self.marketPage._check_collection(collectionID):
            raise errors.NotValidQuerry(f"CollectionID {collectionID}")

        if collectionID in self.collections.keys():
            raise errors.General(
                f"Collection {collectionID} is already in monitor")

        self.collections[collectionID] = CollectionData(
            collectionID, rankID, FilterData(**filters))

    def remove_collection(self, collectionID: str):
        if not collectionID in self.collections:
            raise errors.NotValidQuerry(f"CollectionID {collectionID}")

        self.collections.pop(collectionID)

    def load_collections(self, filePath: str):
        with open(filePath, 'r') as f:
            for rawLine in f.readlines():
                if rawLine[0] == ';':
                    continue

                rawLine = rawLine.replace('\n', '')
                ids, kwargs = rawLine.split(', ')
                ids = ids.split(' ')
                kwargs = kwargs.split(' ')

                collectionID = ids[0]
                rankID = ids[1] if len(ids) == 2 else collectionID.replace('_', '')
                filters = parse_kwargs(kwargs)

                self.add_collection(collectionID, rankID, **filters)
