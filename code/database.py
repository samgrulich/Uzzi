import os 
import enum
import time
import json


class DataLoader:
    def _load_file(self, id: str, path: os.path, default_obj) -> bool:
        file_name = f'{id}.json'
        file_path = os.path.join(path, file_name)
        self.file_path = file_path
        result = False

        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump(default_obj, f)
                result = True

        with open(file_path, 'r') as f:
            self.data = json.load(f) 

        return result


    def _save_file(self, file_path):
        with open(file_path, 'w') as f:
                json.dump(self.data, f)



class HistoryLogType(enum.Enum):
    add = 0
    update = 1
    remove = 2



class HistoryLog(DataLoader):
    empty_log = {}

    def __init__(self, id: str='nft_db0_log', path: str='') -> None:
        if path == '':
            path = os.path.relpath('DBs/logs/')

            if not os.path.lexists(path):
                os.mkdir(path)
        
        self.id = id
        self.path = path

        self._load_file(id, path)

        print(len(self.data))


    def add_log(self, type: HistoryLogType, data):
        #print('adding e_type: ', type)
        actual_time = time.time_ns()

        if not actual_time in self.data.keys():
            self.data[actual_time] = []    
        self.data[actual_time].append({'e_type': type.value, 'data': data})


    def save(self):
        self._save_file(self.file_path)


    def _load_file(self, id: str, path: os.path) -> bool:
        return super()._load_file(id, path, HistoryLog.empty_log)



class DataBase(DataLoader):
    empty_db = {'ids': [0], 'data': {}}

    def __init__(self, id: str='nft_db0', path: str='') -> None:
        if path == '':
            path = os.path.relpath('DBs/')

            if not os.path.lexists(path):
                os.mkdir(path)
        
        self.id = id
        self.log = HistoryLog(f'{id}_log')
        self.path = path

        self._load_file(id, path)


    def save(self):
        self.log.save()
        self._save_file(self.file_path)


    def add(self, data: dict):
        id = data['id']

        if id in self.data['ids']:
            self._update(id, data)
        else:
            self._add(id, data)

    
    def remove(self, id: int):
        if not id in self.data['ids']:
            raise IndexError('Object is not i database')
        else:
            self.data['ids'].remove(id)
            del self.data['data'][id]

    
    def _add(self, id: int, data: dict):
        self.data['ids'].append(id)
        self.data['data'][id] = data
        self.log.add_log(HistoryLogType.add, data)


    def _update(self, id: int, new_data: dict) -> bool:
        print(str(id))
        old_data = self.data['data'][str(id)]
        print(id, old_data)
        result = False

        for key in new_data.keys():
            if key in old_data.keys():
                new_value = new_data[key]
                if not old_data[key] == new_value:
                    self.data['data'][str(id)] = new_value
                    result = True

        if result:
            self.log.add_log(HistoryLogType.update, new_data)

        return result

    
    def _load_file(self, id: str, path: os.path) -> bool:
        return super()._load_file(id, path, DataBase.empty_db)
