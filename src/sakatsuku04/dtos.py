from pydantic import BaseModel, ConfigDict, computed_field
from pydantic.alias_generators import to_camel

from .utils import is_album_player


EXP2LV = (0, 65, 140, 225, 320, 425, 540, 665, 800, 945, 1105, 1275, 1455, 1645, 1845, 2055, 2275, 2505, 2745, 2995, 3255, 3525, 3805, 4095, 4395, 4705, 5025, 5355, 5695, 6045, 6420, 6805, 7200, 7605, 8020, 8445, 8880, 9325, 9780, 10245, 10725, 11215, 11715, 12225, 12745, 13275, 13815, 14365, 14925, 15495, 16130, 16776, 17433, 18101, 18780, 19470, 20171, 20883, 21606, 22340, 23145, 23962, 24791, 25632, 26485, 27350, 28227, 29116, 30017, 30930, 31855, 32792, 33741, 34702, 35675, 36660, 37657, 38666, 39687, 40720, 41765, 42822, 43891, 44972, 46065, 47170, 48287, 49416, 50557, 51710, 52880, 54063, 55259, 56468, 57690, 58925, 60173, 61434, 62708, 63995, 65295, 65535)
ABI_PHY = (20, 21, 22, 23)
ABI_SYS = (41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53)
ABI_TAC = (36, 37, 38, 39, 40)
ABI_OFF = (6, 8, 9, 10, 11, 12, 13, 14, 21)
ABI_GK = (2, 3, 17, 18, 19, 28)
ABI_DEF = (3, 7, 14, 15, 16, 20)
ABI_STA = (24, )
ABI_MEN = (0, 1, 2, 3, 4, 5, 6, 7, 24)
GROW_PHY = (20, 21, 22, 23, 24)
GROW_TEC = (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19)
GROW_MEN = (0, 1, 2, 3, 4, 25, 63)


class BaseDto(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class ClubDto(BaseDto):
    club_name: str
    year: int
    month: int
    date: int
    day: int
    funds_high: int
    funds_low: int
    manager_name: str
    difficulty: int
    seed: int

    def combo_funds(self) -> int:
        return self.funds_high * 10000 + self.funds_low


class MyTeamPlayerDto(BaseDto):
    id: int
    name: str
    pos: int

    @computed_field
    @property
    def is_album(self) -> bool:
        return is_album_player(self.id)


class PlayerAbilityDto(BaseDto):
    index: int
    current: int
    current_max: int
    max: int


class MyPlayerDto(BaseDto):
    index: int
    id: int
    age: int
    number: int
    name: str
    born: int
    abroad_times: int
    height: int
    foot: int
    rank: int
    pos: int
    grow_type_phy: int
    grow_type_tec: int
    grow_type_sys: int
    tone_type: int
    cooperation_type: int
    style: int
    abilities: list[PlayerAbilityDto]
    desire: int
    pride: int
    ambition: int
    patient: int
    persistence: int
    jl_factor: int

    @computed_field
    @property
    def is_album(self) -> bool:
        return is_album_player(self.id)

    @computed_field
    @property
    def hexagon(self) -> list[int]:
        return [
            calc_off(self),
            calc_gk(self) if self.pos == 0 else calc_def(self),
            calc_sta(self),
            calc_phy(self),
            calc_sys(self),
            calc_tac(self),
            calc_off(self, 1),
            calc_gk(self, 1) if self.pos == 0 else calc_def(self, 1),
            calc_sta(self, 1),
            calc_phy(self, 1),
            calc_sys(self, 1),
            calc_tac(self, 1),
            calc_off(self, 2),
            calc_gk(self, 2) if self.pos == 0 else calc_def(self, 2),
            calc_sta(self, 2),
            calc_phy(self, 2),
            calc_sys(self, 2),
            calc_tac(self, 2),
        ]


class TeamDto(BaseDto):
    index: int
    name: str
    friendly: int


class OtherTeamPlayerDto(BaseDto):
    id: int
    age: int
    ability_graph: int
    number: int
    name: str
    rank: str
    pos: str
    cooperation_type: str
    tone_type: str
    grow_type_phy: str
    grow_type_tec: str
    grow_type_sys: str

    @computed_field
    @property
    def is_album(self) -> bool:
        return is_album_player(self.id)


def player_hexagon_convert(input_value: int) -> int:
    return (min(input_value + 10, 90) * 100) // 90


def lv2dot(level_value: float) -> int:
    return (min((100 * level_value * 95) // 90 + 5, 100) * 32) // 100


def ability2lv(exp: int) -> int:
    level, loop_limit = (1, 0x32) if exp < 16776 else (0x33, 0x65)
    while level <= loop_limit:
        level += 1
        if EXP2LV[level] >= exp:
            break
    return level - 1


def _calc_avg(player: MyPlayerDto, indices: tuple[int], mode: int) -> int:
    total = 0
    count = 0
    for i in indices:
        ability = player.abilities[i]
        if mode == 0:
            lv = ability2lv(ability.current)
        elif mode == 1:
            lv = ability2lv(ability.current_max)
        elif mode == 2:
            lv = ability2lv(ability.max)
        else:
            raise ValueError(f"Invalid mode: {mode}")
        total += lv
        count += 1
    return total // count if count else 0


def calc_off(player: MyPlayerDto, mode: int = 0) -> int:
    return _calc_avg(player, ABI_OFF, mode)

def calc_def(player: MyPlayerDto, mode: int = 0) -> int:
    return _calc_avg(player, ABI_DEF, mode)

def calc_gk(player: MyPlayerDto, mode: int = 0) -> int:
    return _calc_avg(player, ABI_GK, mode)

def calc_phy(player: MyPlayerDto, mode: int = 0) -> int:
    return _calc_avg(player, ABI_PHY, mode)

def calc_sys(player: MyPlayerDto, mode: int = 0) -> int:
    return _calc_avg(player, ABI_SYS, mode)

def calc_tac(player: MyPlayerDto, mode: int = 0) -> int:
    return _calc_avg(player, ABI_TAC, mode)

def calc_sta(player: MyPlayerDto, mode: int = 0) -> int:
    return _calc_avg(player, ABI_STA, mode)
