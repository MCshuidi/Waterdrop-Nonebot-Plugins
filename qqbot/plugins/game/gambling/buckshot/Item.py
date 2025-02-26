from abc import ABC, abstractmethod

from .Player import Player

class Item(ABC):
    @property
    @abstractmethod
    def item_name(self) -> str:
        pass
    @abstractmethod
    def active_item(self , use_player : Player , oppoment_player : Player) -> None:
        pass