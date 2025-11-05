from dataclasses import dataclass

from ..dtos import ClubDto, CoachDto, MyPlayerDto, OtherTeamPlayerDto, PlayerAbilityDto, ScoutDto, TownDto
from ..io import IntByteField, StrByteField
from ..objs import Coach, Player, Scout


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
    team_status: IntByteField

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
            team_status=self.team_status.value,
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
    return_days: IntByteField
    height: IntByteField
    foot: IntByteField
    rank: IntByteField
    pos: IntByteField
    base_pos: IntByteField
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
    wave_type: IntByteField
    salary: IntByteField
    offer_years_passed: IntByteField
    offer_years_total: IntByteField
    test: IntByteField = IntByteField(0, 0, 0)
    un: list[int]
    kan: IntByteField
    moti: IntByteField
    power: IntByteField
    super_sub: IntByteField
    wild_type: IntByteField
    weak_type: IntByteField
    tired_type: IntByteField
    pop: IntByteField
    comp_money: IntByteField
    comp_discord: IntByteField
    comp_staff: IntByteField
    comp_usage: IntByteField
    comp_result: IntByteField
    comp_status: IntByteField
    comp_euipment: IntByteField
    tired: IntByteField
    status: IntByteField
    condition: IntByteField
    explosion_exp: IntByteField
    explosion_level: IntByteField
    explo_countdown: IntByteField
    explo_pending_reason: IntByteField
    explo_final_reason: IntByteField

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
            wave_type=self.wave_type.value,
            sp_comment=player.sp_comment,
            salary_high=self.salary.value * 100 // 10000,
            salary_low=self.salary.value * 100 % 10000,
            offer_years_passed=self.offer_years_passed.value,
            offer_years_total=self.offer_years_total.value,
            power=self.power.value,
            moti=self.moti.value,
            kan=self.kan.value,
            super_sub=self.super_sub.value,
            wild_type=self.wild_type.value,
            weak_type=self.weak_type.value,
            tired_type=self.tired_type.value,
            pop=self.pop.value,
            comp=[self.comp_money.value, self.comp_discord.value, self.comp_staff.value, self.comp_usage.value, self.comp_result.value, self.comp_status.value, self.comp_euipment.value],
            tired=self.tired.value,
            status=self.status.value,
            condition=self.condition.value,
            explosion_exp=self.explosion_exp.value,
            explosion_level=self.explosion_level.value,
            explo_countdown=self.explo_countdown.value,
            explo_pending_reason=self.explo_pending_reason.value,
            explo_final_reason=self.explo_final_reason.value,
        )


@dataclass
class OtherPlayer:
    id: IntByteField
    age: IntByteField
    ability_graph: IntByteField | None = None
    number: IntByteField | None = None

    def to_dto(self):
        player = Player(self.id.value)
        _number = 0 if not self.number else self.number.value
        return OtherTeamPlayerDto(
            id=self.id.value,
            age=self.age.value,
            # ability_graph=self.ability_graph.value,
            number=_number,
            name=player.name,
            rank=player.rank,
            pos=player.pos,
            born=player.born,
            cooperation_type=player.cooperation_type,
            tone_type=player.tone_type,
            style=player.style,
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


class Town:
    living: IntByteField
    economy: IntByteField
    sports: IntByteField
    env: IntByteField
    population: IntByteField
    price: IntByteField
    traffic_level: IntByteField
    soccer_pop: IntByteField
    soccer_level: IntByteField
    town_type: IntByteField

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
            town_type=self.town_type.value,
        )


@dataclass
class MyScout:
    id: IntByteField
    age: IntByteField | None = None
    saved_name: StrByteField | None = None
    abilities: list[IntByteField] | None = None
    offer_years: IntByteField | None = None
    area1: IntByteField | None = None
    area2: IntByteField | None = None

    def to_dto(self) -> ScoutDto:
        return ScoutDto(
            id=self.id.value,
            name=self.saved_name.value if self.saved_name else "",
        )

    def to_dto_with_name(self, id: int) -> ScoutDto:
        return ScoutDto(
            id=self.id.value,
            name=Scout.name(id),
        )


@dataclass
class MyCoach:
    id: IntByteField
    age: IntByteField | None = None
    saved_name: StrByteField | None = None
    offer_years: IntByteField | None = None

    def to_dto(self) -> CoachDto:
        return CoachDto(
            id=self.id.value,
            name=self.saved_name.value if self.saved_name else "",
            age=self.age.value if self.age else None,
            offer_years=self.offer_years.value if self.offer_years else None,
        )

    def to_dto_with_name(self, id: int) -> CoachDto:
        return CoachDto(
            id=self.id.value,
            name=Coach.name(id),
            age=self.age.value if self.age else None,
            offer_years=self.offer_years.value if self.offer_years else None,
        )
