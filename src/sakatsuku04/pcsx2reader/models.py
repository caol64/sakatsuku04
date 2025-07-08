from dataclasses import dataclass
from ..dtos import ClubDto, MyPlayerDto, OtherTeamPlayerDto, PlayerAbilityDto
from ..objs import Player
from ..io import IntByteField, StrByteField


class Club:
    year: IntByteField
    month: IntByteField
    date: IntByteField
    day: IntByteField
    funds: IntByteField
    manager_name: StrByteField
    club_name: StrByteField
    difficulty: IntByteField
    seed: IntByteField

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
    current: IntByteField
    current_max: IntByteField
    max: IntByteField


class MyPlayer:
    index: int
    id: IntByteField
    age: IntByteField
    number: IntByteField
    name: StrByteField
    abilities: list[MyPlayerAbility]
    born: IntByteField
    born2: IntByteField
    abroad_times: IntByteField
    abroad_days: IntByteField
    height: IntByteField
    foot: IntByteField
    rank: IntByteField
    pos: IntByteField
    pos2: IntByteField
    grow_type_phy: IntByteField
    grow_type_tec: IntByteField
    grow_type_sys: IntByteField
    tone_type: IntByteField
    cooperation_type: IntByteField
    style: IntByteField
    style_equip: IntByteField
    style_learned1: IntByteField
    style_learned2: IntByteField
    style_learned3: IntByteField
    style_learned4: IntByteField
    magic_value: IntByteField
    desire: IntByteField
    pride: IntByteField
    ambition: IntByteField
    patient: IntByteField
    persistence: IntByteField
    test: IntByteField = IntByteField(0, 0, 0)
    un: list[int]

    def set_style(self, style_index: int):
        new_int = (self.style_learned2.value << 32) | self.style_learned1.value
        new_int |= (1 << style_index)
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
        )


@dataclass
class OtherPlayer:
    id: IntByteField
    age: IntByteField
    ability_graph: IntByteField
    number: IntByteField = None

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
            cooperation_type=player.cooperation_type,
            tone_type=player.tone_type,
            grow_type_phy=player.grow_type_phy,
            grow_type_tec=player.grow_type_tec,
            grow_type_sys=player.grow_type_sys,
        )


@dataclass
class OtherTeam:
    index: int
    id: IntByteField
    friendly: IntByteField
    unknown1: IntByteField
    unknown2: IntByteField
    players: list[OtherPlayer]
