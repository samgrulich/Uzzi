import asyncio
import meden
import time
from crossplatform import core, core_types, network
from crossplatform import core_exceptions as errors

from typing import List, Dict

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

        result = {}
        startTime = time.time_ns()
        loopTime = time.time_ns()

        for i, collection in enumerate(self.collections.values()):
            snapshot = self.marketPage.get_snapshot(
                collection.id, collection.rankID)
            snapshot = collection.update_snapshot(snapshot)

            if not i % 2:
                # limit to 2 QPS
                now = time.time_ns()
                deltaTime = now - startTime
                # interval = 1e9 / (len(network.proxies))
                interval = 1e9 
                waitInterval = (interval - deltaTime) / 1e9

                if deltaTime < interval:
                    print("wainting for ", waitInterval, " seconds")
                    await asyncio.sleep(waitInterval)
                
                startTime = time.time_ns()

            if snapshot.isEmpty():
                continue

            result[collection.id] = snapshot
        
        print("Total loop time is ", (time.time_ns() - loopTime) / 1e9, " s")

        if len(result):
            debug_print(f"Update result len: {len(result)}", "Monitor")

        return result

    def update_collection(self, collection: CollectionData) -> core.Snapshot:
        snapshot = self.marketPage.get_snapshot(collection.id, collection.rankID)
        snapshot = collection.update_snapshot(snapshot)

        return snapshot

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
                splitLine = rawLine.split(' ')

                collectionID = splitLine[0]
                rankID = collectionID.replace('_', '')
                filters = parse_kwargs(splitLine[1:])

                self.add_collection(collectionID, rankID, **filters)
