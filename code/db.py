import os
import time
import json
import enum



class Data:
    def __init__(self, dict_initiator:dict=None) -> None:
        """
        Data class for easier data manipulation
        """

        #variables
        self.max_cache_items = 20

        #data - lists/dicts
        self.id_cache = []
        self.item_cache = []
        self.perma = {}    


        if dict_initiator:
            for key, item in dict_initiator.items():
                self.__setattr__(key, item)


    # public
    #region

    def Add(self, data, id:int=None) -> None:
        """
        Append new Data to your existing Data set
        \t (if id is not passed then current time is used)
        """
        if not id:
            id = time.time_ns()

        id_cache = self.id_cache
        item_cache = self.item_cache

        id_cache.insert(0, id)
        item_cache.insert(0, data)

        # move old chached items to perma data
        if len(self.item_cache) >= self.max_cache_items:
            old_id = id_cache.pop(-1)
            old_item = item_cache.pop(-1)

            self.perma[old_id] = old_item

        self.id_cache = id_cache
        self.item_cache = item_cache


    def Request(self, id) -> dict:
        """
        Search for your Data by ID
        \t (returns None if not found)
        """
        id_cache = self.id_cache

        if id in id_cache:
            id_index = id_cache.index(id)
            return self.item_cache[id_index]
        elif id in self.perma.keys():
            return self.perma[id] 

        return None
    
    
    @property
    def all_data(self) -> dict:
        """
        Extracts all data
        \t returns all data (cache + permanent)
        """
        cache_data = self.perma

        for id, item in self.id_cache, self.item_cache:
            cache_data[id] = item

        return cache_data
    #endregion



class DataLoader:
    @staticmethod
    def Save(data:Data, path:str) -> bool:
        """
        Save your Data object to file
        \t returns bool - whether action was successful
        """
        path = os.path.abspath(path)

        if not os.path.exists(os.path.dirname(path)):
            return False

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data.__dict__, f, ensure_ascii=False, indent=4)

        return True

    
    @staticmethod
    def Load(path:str, type_:type) -> Data:
        """
        Load Data form file
        \t returns None if action was unsuccessful 
        """
        if not os.path.exists(path):
            return None

        with open(path, 'r', encoding='utf-8') as f:
            return Data(json.load(f))



class Log(Data):
    class Type(enum.Enum):
        add=0
        update=1
        remove=2

    def __init__(self, intiator:dict=None) -> None:
        """
        List of changes
        """
        super().__init__(intiator)
        self.max_cache_items = 40

    
    def Add(self, type:Type, id:int=None, nft_data:dict=None, save_old_data=False) -> None:
        """
        Add new log
        """
        data = {'type': type.value, 'id': id, 'time': time.time_ns()}

        if save_old_data and type in (Log.Type.update, Log.Type.remove):
            if not nft_data:
                return

            data['data'] = nft_data

        return super().Add(data, id=id)

    
    def Request(self, id, **kwargs) -> dict:
        #TODO: implement kwargs querrying
        return super().Request(id)



class Database(Data):
    def __init__(self, id, dir_path:str='', initiator:dict=None) -> None:
        super().__init__(initiator)
        
        dir_path = os.path.abspath(os.path.normpath(dir_path))
        
        self.id = id
        self.dirpath = dir_path
        self.log = None

        if os.path.exists(os.path.join(dir_path, f'{id}_db.json')):
            self.Load()

        if not self.log:
            self.log = Log()

    
    # public
    #region

    def Add(self, data) -> None:
        """
        Add new data to database \n
        \t (Actually there is check so you can updata data too, but just because you can that doesn't mean you should)
        """
        id = data['id']

        if id in self.id_cache or id in self.perma.keys():
            self.Update(data)

            return

        self.log.Add(Log.Type.add, id)

        super().Add(data, id=id)


    def Update(self, data:dict) -> None:
        """
        Update value in database, `DATA MUST INCLUDE ID` 
        """
        id = data['id']

        success = self._update(id, data)

        if success:
            self.log.Add(Log.Type.update, id, data)


    def Remove(self, id) -> None:
        """
        Remove value from Database
        """
        data = self.Request(id)

        if not data:
            return 

        self._remove(id)


    def Request(self, id) -> dict:
        # TODO
        return super().Request(id)


    def Save(self) -> None:
        """
        Save database /w log to file
        """
        DataLoader.Save(self.log, os.path.join(self.dirpath, f'{self.id}_log.json'))
        self.log = {}
        DataLoader.Save(self, os.path.join(self.dirpath, f'{self.id}_db.json'))

        print(f'{os.path.abspath(os.path.join(self.dirpath, f"{self.id}_db.json"))} databse saved')
    
    
    def Load(self) -> None:
        """
        Load database, log files
        """

        log = DataLoader.Load(os.path.join(self.dirpath, f'{id}_log.json'), Log)
        self = DataLoader.Load(os.path.join(self.dirpath, f'{self.id}_db.json'), Database)

        if not log:
            log = Log()

        self.log = log

    #endregion
    
    
    # private
    #region

    def _update(self, id, data) -> bool:
        """
        Update value at id \n
        with cache/perma check
        """
        id_cache = self.id_cache

        if id in self.id_cache:
            id_index = id_cache.index(id)

            if self.item_cache[id_index] == data:
                return False

            self.item_cache[id_index] = data

        elif id in self.perma:
            if self.perma[id] == data:
                return False

            self.perma[id] = data

        return True


    def _remove(self, id) -> None:
        """
        Update value at id \n
        with cache/perma check
        """

        id_cache = self.id_cache

        if id in self.id_cache:
            id_index = id_cache.index(id)
            
            self.id_cache.pop(id_index)
            self.item_cache.pop(id_index)

        elif id in self.perma:
            del self.perma[id]

    #endregion

