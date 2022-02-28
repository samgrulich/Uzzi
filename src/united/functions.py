"""
Group of unique functions, works across all nft pages

Additional functions that which work with basic models, 
you can use custom ones, but its not recommended.
They are all grouped under static classes so access the 
functions through them 
(you don't have to instantiate the classes)

Classes
-------
* DataLoader \n
    Functions for code-file operations (saving, loading objects)
* TableLoader \n 
    Load dictionary from filter table file
"""


import os
import csv
import json


class DataLoader:
    """
    Functions used for file operations

    Methods
    -------
    Save(data, path) -> None
        Save object to file
    Load(out_obj, path) -> object
        Load object from file
    """

    @staticmethod
    def Save(data: object, path: str) -> None:
        """
        Save object to file

        Arguments
        ---------
        data : object
            object that will be saved
        path : str
            where the file will be saved
        """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data.__dict__, f, ensure_ascii=False, indent=4)

    @staticmethod
    def Load(out_obj: object, path: str) -> object:
        """
        Load object form file

        Attributes
        ----------
            out_obj : object
                object where the saved file will be loaded
            path : str
                path to file

        Returns
        -------
        object
            loaded object, `None` if action was unsuccessful 
        """
        if not os.path.exists(path):
            return None

        with open(path, 'r', encoding='utf-8') as f:
            return out_obj.__dict__.update(json.load(f))


class TableLoader:
    """
    Functions used for table file operations, mainly loading

    Methods
    -------
    Load(path, out_obj)
        Load dictionary object from table (csv) file
    """
    @staticmethod
    def Load(path: str, out_obj: dict = None) -> dict:
        """
        Load dictionary from object, returns None if file doesn't exist

        Arguments 
        ---------
        path : str
            path to file
        out_obj : dict - Optional
            dictionary where the result will be ouputed
        """

        out_obj = out_obj if out_obj else {}
        path = os.path.abspath(path)

        if not os.path.exists(path):
            return None

        with open(path, 'r') as file:
            reader = csv.reader(file)

            for row in reader:
                row_key = row[0]
                row_list = list(filter(lambda value: bool(value), row[1:]))
                row_dict = {}

                for i, att_pair in enumerate(row_list):
                    att_pair = att_pair.replace('\n', '')
                    key, val = att_pair.split('=')
                    row_dict[key] = val

                out_obj[row_key] = row_dict

        return out_obj
