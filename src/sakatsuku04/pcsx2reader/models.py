from dataclasses import dataclass
from ..dtos import ClubDto, MyPlayerDto, OtherTeamPlayerDto
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

    def to_dto(self):
        return ClubDto(
            club_name=self.club_name.value,
            year=self.year.value - 2003,
            month=self.month.value,
            date=self.date.value,
            day=self.day.value,
            funds=self.funds.value,
            manager_name=self.manager_name.value,
            difficulty=self.difficulty.value,
        )


class MyPlayer:
    index: int
    id: IntByteField
    age: IntByteField
    number: IntByteField
    name: StrByteField
    # abilities: list[MyPlayerAbility]
    # born: IntBitField
    # born2: IntBitField
    # abroad_times: IntBitField
    # abroad_days: IntBitField
    # height: IntBitField
    # foot: IntBitField
    # rank: IntBitField
    pos: IntByteField
    # pos2: IntBitField
    # grow_type_phy: IntBitField
    # grow_type_tec: IntBitField
    # grow_type_bra: IntBitField
    # tone_type: IntBitField
    # cooperation_type: IntBitField
    # style: IntBitField
    # style_equip: IntBitField
    # style_learned1: IntBitField
    # style_learned2: IntBitField
    # style_learned3: IntBitField
    # style_learned4: IntBitField
    # magic_value: IntBitField
    # test: IntBitField = IntBitField(0, 0, 0)
    # un: list[int]

    def to_dto(self) -> MyPlayerDto:
        return MyPlayerDto(
            index=self.index,
            id=self.id.value,
            age=self.age.value,
            number=self.number.value,
            name=self.name.value,
            pos=self.pos.value,
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
