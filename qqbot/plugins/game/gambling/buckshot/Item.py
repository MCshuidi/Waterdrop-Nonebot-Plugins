from abc import ABC, abstractmethod

from .Player import Player

class Item(ABC):
    @abstractmethod
    def active_item(self , use_player : Player , oppoment_player : Player) -> None:
        pass
    @abstractmethod
    def get_name(self) -> str:
        pass