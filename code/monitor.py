import time

from code.data import Database, NFTParser, turbo_check



class Monitor:
    def __init__(self, collection:str, **filters) -> None:
        self.collection = collection
        self.filters = filters

        self.database = Database(collection, './DBs/').Load()
        self.nft_parser = NFTParser(collection)

        valid, nft_page, rank_page = self.get_support()
        self.valid = valid
        self.nft_page = nft_page
        self.rank_page = rank_page


    def update(self) -> list[dict]:
        "Add new nfts on page to databse, returns added nfts"
        changed = turbo_check(self.collection, self.database, self.nft_parser)

        if not changed:
            return None

        # database update
        nfts = self.nft_parser.parse_all()
        nfts.reverse()

        for nft in nfts:
            self.database.Add(nft.vars())

        self.database.Save()

        # update request
        updated_nfts = self.database.Request()
        return updated_nfts


    def set_filters(self, **filters) -> None:
        "Cahnge nft filters"
        self.filters = filters


    def get_support(self) -> tuple[bool, str, str]:
        "Check if monitor is valid, then nft page name and then rank support"
        nft_support = self.nft_parser.supported_page
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
