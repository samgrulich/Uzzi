import os

# from data import Database, NFTParser, turbo_check, get_last_nft
# from solanart_funcs import Collection, get_nfts, SolanartSnapshot, parse_snapshot, filter_snapshot
import solanart
from united import objects


class Monitor:
    def __init__(self, collection_id: str, **filters) -> None:
        self.collection = solanart.SolCollection(collection_id)

        old_nfts = solanart.get_nfts(collection_id)
        self.old_snap = objects.Snapshot(old_nfts)

        self.filters = filters

    def update(self) -> list[dict]:
        new_nfts = solanart.get_nfts(self.collection.id)
        new_snap = objects.Snapshot(new_nfts)

        # self.old_snap.list.pop(0)
        # self.old_snap.ids.pop(0)

        # self.old_snap.list.pop(-1)
        # self.old_snap.ids.pop(-1)

        result = new_snap - self.old_snap
        parsed_result = solanart.parse_snapshot(result, self.collection)
        filtered_result = solanart.filter_snapshot(
            parsed_result, **self.filters)

        self.old_snap = new_snap

        return filtered_result

    def set_filters(self, **filters) -> None:
        "Cahnge nft filters"
        self.filters = filters

    def get_support(self) -> tuple[bool, str, str]:
        "Check if monitor is valid, then nft page name and then rank support"
        nft_support = self.nft_parser.supported_page

        if not nft_support:
            return [False, 'None', 'None']

        rank_support = self.nft_parser.supported_page.rank_parser.supported_page

        nft_page_name = 'None'
        rank_page_name = 'None'

        # validity of this monitor
        valid = nft_support

        if nft_support:
            nft_page_name = nft_support.id

        if rank_support:
            rank_page_name = rank_support.id

        return (valid, nft_page_name, rank_page_name)


# monitor = Monitor('cyberpharmacist', Background=10)
