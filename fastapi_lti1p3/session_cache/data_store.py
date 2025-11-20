from typing import Literal, Any, Union
from ..models.cache_models import Session, Nonce

class DataStore:
    def __init__(self):
        self._data = {}

    async def append(self, value: Union[Session, Nonce]) -> bool:
        """
        Adds item to data store and returns True if primary key of Session/Nonce obj is unique, else returns False
        """
        if value not in self._data.values():
            self._data[str(value)] = value
            return True
        
        return False
    
    def __getitem__(self, primary_key: str) -> Union[Session, Nonce, None]:
        return self._data.get(primary_key)
    
    def __setitem__(self, key: str, value: dict) -> Union[Session, Nonce]:
        """
        updates attributes of item at key
        """
        item = self[key]
        return item.update(**value) if item else item
    
    def __delitem__(self, key: str) -> None:
        try:
            del self._data[key]
        except KeyError:
            return None