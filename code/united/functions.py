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
"""


import os
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
