from .Item import Item
from .Main import MAX_ITEM_COUNT

class Player:
    player_id : int
    player_heart : int
    player_soul_heart : int = 0
    player_max_heart : int
    player_locked_round : int = 0
    player_items : list[Item] = []
    def __init__(self , player_id : int):
        self.player_id = player_id
    def init_table(self , player_max_heart : int) -> None:
        self.player_heart = player_max_heart
        self.player_max_heart = player_max_heart
    def if_death(self) -> bool:
        return self.player_heart < 0 or (self.player_heart == 0 and self.player_soul_heart == 0)
    def earn_heart(self , count : int) -> None:
        self.player_heart = min(self.player_heart + count , self.player_max_heart)
    def earn_soul_heart(self , count : int) -> None:
        self.player_soul_heart += count
    def cal_damage(self , damage : int) -> None:
        if self.player_soul_heart > damage:
            self.player_soul_heart -= damage
        else:
            damage -= self.player_soul_heart
            self.player_soul_heart = 0
            self.player_heart -= damage
    def add_item(self , item : Item) -> None:
        if len(self.player_items) == MAX_ITEM_COUNT:
            return
        self.player_items.append(item)
    def get_item(self , item_name : str) -> Item | None:
        for i in range(len(self.player_items)):
            if self.player_items[i].get_name() == item_name:
                return self.player_items.pop(i)
        return None