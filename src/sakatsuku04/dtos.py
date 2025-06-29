from pydantic import BaseModel, ConfigDict
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
    fund_heigh: int
    fund_low: int
    manager_name: str
    difficulty: int


class PlayerAbilityDto(BaseDto):
    index: int
    current: int
    current_max: int
    max: int
    name: str


class MyPlayerDto(BaseDto):
    index: int
    id: int
    age: int
    number: int
    name: str
    # abilities: list[PlayerAbilityDto]
    # born: int
    # born2: int
    # abroad_times: int
    # abroad_days: int
    # height: int
    # foot: int
    # rank: int
    # pos: int
    # pos2: int
    # grow_type_phy: int
    # grow_type_tec: int
    # grow_type_bra: int
    # tone_type: int
    # cooperation_type: int
    # style: int
    # style_equip: int
    # style_learned1: int
    # style_learned2: int
    # style_learned3: int
    # style_learned4: int
    # magic_value: int
    # prefer_foot: str
    # readable_rank: str
    # readable_style: str
    # readable_born: str
    # readable_cooperation_type: str
    # readable_pos: str
    # readable_tone_type: str


class TeamDto(BaseDto):
    index: int
    name: str
    friendly: int


class TeamsWithRegionDto(BaseDto):
    region: str
    teams: list[TeamDto]


class OtherTeamPlayerDto(BaseDto):
    id: int
    age: int
    ability_graph: int
    number: int
    name: str
    rank: str
    pos: str
    team_work: str
    tone_type: str
    grow_type_phy: str
    grow_type_tech: str
    grow_type_sys: str
