from pydantic import BaseModel, ConfigDict, computed_field
from pydantic.alias_generators import to_camel


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
    funds: int = None
    manager_name: str
    difficulty: int

    @computed_field
    @property
    def funds_high(self) -> int:
        return self.funds // 10000

    @computed_field
    @property
    def funds_low(self) -> int:
        return self.funds % 10000

    def set_funds(self):
        self.funds = self.funds_high * 10000 + self.funds_low


class PlayerAbilityDto(BaseDto):
    index: int
    current: int
    current_max: int
    max: int
    current_percent: float
    current_max_percent: float
    max_percent: float


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
