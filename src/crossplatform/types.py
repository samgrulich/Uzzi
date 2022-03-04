import enum

class MarketPageAPIs(enum.Enum):
    all_collections = 0
    collection_floor = 1
    collection_info = 2
    snapshot_query = 3

class RankPageAPIs(enum.Enum):
    all_collections = 0
    collection_full = 1
    collection_rate = 2