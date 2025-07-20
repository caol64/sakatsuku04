from dataclasses import dataclass

from ..dtos import ClubDto, MyPlayerDto, OtherTeamPlayerDto, PlayerAbilityDto, ScoutDto, TownDto
from ..io import IntBitField, IntByteField, StrBitField, StrByteField
from ..objs import Player, Scout


@dataclass
class Saka04SaveEntry:
    name: str
    main_save_entry: bytes
    save_head_entry: bytes
    sys_icon_entry: bytes


class Header:
    u1: IntByteField
    u2: IntByteField
    year: IntByteField
    month: IntByteField
    date: IntByteField
    day: IntByteField
    club_name: StrByteField
    club_name1: StrByteField


class Club:
    year: IntBitField
    month: IntBitField
    date: IntBitField
    day: IntBitField
    funds: IntBitField
    manager_name: StrBitField
    club_name: StrBitField
    difficulty: IntBitField
    seed: IntBitField

    def to_dto(self):
        return ClubDto(
            club_name=self.club_name.value,
            year=self.year.value - 2003,
            month=self.month.value,
            date=self.date.value,
            day=self.day.value,
            funds_high=self.funds.value // 10000,
            funds_low=self.funds.value % 10000,
            manager_name=self.manager_name.value,
            difficulty=self.difficulty.value,
            seed=self.seed.value,
        )


@dataclass
class MyPlayerAbility:
    index: int
    current: IntBitField
    current_max: IntBitField
    max: IntBitField


class MyPlayer:
    index: int
    id: IntBitField
    age: IntBitField
    number: IntBitField
    name: StrBitField
    abilities: list[MyPlayerAbility]
    born: IntBitField
    born2: IntBitField
    abroad_times: IntBitField
    injury_days: IntBitField
    height: IntBitField
    foot: IntBitField
    rank: IntBitField
    pos: IntBitField
    base_pos: IntBitField
    grow_type_phy: IntBitField
    grow_type_tec: IntBitField
    grow_type_sys: IntBitField
    tone_type: IntBitField
    cooperation_type: IntBitField
    style: IntBitField
    style_equip: IntBitField
    style_learned1: IntBitField
    style_learned2: IntBitField
    style_learned3: IntBitField
    style_learned4: IntBitField
    magic_value: IntBitField
    desire: IntBitField
    pride: IntBitField
    ambition: IntBitField
    patient: IntBitField
    persistence: IntBitField
    grow_type_id: IntBitField
    salary: IntBitField
    offer_years_passed: IntBitField
    offer_years_total: IntBitField
    test: IntBitField = IntBitField(0, 0, 0)
    un: list[int]

    def __init__(self, index: int):
        self.index = index
        self.abilities = list()
        self.un = list()

    def set_style(self, style_index: int):
        new_int = (self.style_learned2.value << 32) | self.style_learned1.value
        new_int |= 1 << style_index
        self.style_learned1.value = new_int & 0xFFFFFFFF
        self.style_learned2.value = (new_int >> 32) & 0xFFFFFFFF

    def to_dto(self) -> MyPlayerDto:
        abilities = [
            PlayerAbilityDto(
                index=a.index,
                current=a.current.value,
                current_max=a.current_max.value,
                max=a.max.value,
            )
            for a in self.abilities
        ]
        player = Player(self.id.value)
        return MyPlayerDto(
            index=self.index,
            id=self.id.value,
            age=self.age.value,
            number=self.number.value,
            name=self.name.value,
            born=self.born.value,
            abroad_times=self.abroad_times.value,
            height=self.height.value,
            foot=self.foot.value,
            rank=self.rank.value,
            pos=self.pos.value,
            grow_type_phy=self.grow_type_phy.value,
            grow_type_tec=self.grow_type_tec.value,
            grow_type_sys=self.grow_type_sys.value,
            tone_type=self.tone_type.value,
            cooperation_type=self.cooperation_type.value,
            style=self.style.value,
            abilities=abilities,
            desire=self.desire.value,
            pride=self.pride.value,
            ambition=self.ambition.value,
            patient=self.patient.value,
            persistence=self.persistence.value,
            grow_type_id=self.grow_type_id.value,
            sp_comment=player.sp_comment,
            salary_high=self.salary.value * 100 // 10000,
            salary_low=self.salary.value * 100 % 10000,
            offer_years_passed=self.offer_years_passed.value,
            offer_years_total=self.offer_years_total.value,
        )


class MyTeam:
    english_name: StrBitField
    oilis_english_name: StrBitField
    players: list[MyPlayer]
    youth_players: list[MyPlayer]
    my_scouts: list["MyScout"]
    scout_candidates: list["MyScout"]


@dataclass
class OtherPlayer:
    id: IntBitField
    age: IntBitField
    ability_graph: IntBitField
    number: IntBitField = None

    def to_dto(self):
        player = Player(self.id.value)
        return OtherTeamPlayerDto(
            id=self.id.value,
            age=self.age.value,
            ability_graph=self.ability_graph.value,
            number=self.number.value,
            name=player.name,
            rank=player.rank,
            pos=player.pos,
            born=player.born,
            cooperation_type=player.cooperation_type,
            tone_type=player.tone_type,
            grow_type_phy=player.grow_type_phy,
            grow_type_tec=player.grow_type_tec,
            grow_type_sys=player.grow_type_sys,
        )


@dataclass
class OtherTeam:
    index: int
    id: IntBitField
    friendly: IntBitField
    unknown1: IntBitField
    unknown2: IntBitField
    players: list[OtherPlayer]


@dataclass
class MyScout:
    id: IntBitField
    age: IntBitField = None
    saved_name: StrBitField = None
    abilities: list[IntBitField] = None
    offer_years: IntBitField = None
    area1: IntBitField = None
    area2: IntBitField = None

    def to_dto(self):
        return ScoutDto(
            id=self.id.value,
            name=self.saved_name.value,
        )

    def to_dto_with_name(self, id: int):
        return ScoutDto(
            id=self.id.value,
            name=Scout.name(id),
        )


class Town:
    living: IntBitField
    economy: IntBitField
    sports: IntBitField
    env: IntBitField
    population: IntBitField
    price: IntBitField
    traffic_level: IntBitField
    soccer_pop: IntBitField
    soccer_level: IntBitField

    def to_dto(self):
        return TownDto(
            living=self.living.value,
            economy=self.economy.value,
            sports=self.sports.value,
            env=self.env.value,
            population=self.population.value,
            price=self.price.value,
            traffic_level=self.traffic_level.value,
            soccer_pop=self.soccer_pop.value,
            soccer_level=self.soccer_level.value,
        )
