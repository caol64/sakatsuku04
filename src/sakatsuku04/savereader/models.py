from dataclasses import dataclass

from ..dtos import ClubDto, CoachDto, MyPlayerDto, OtherTeamPlayerDto, PlayerAbilityDto, ScoutDto, SponsorDto, TownDto
from ..io import IntBitField, IntByteField, StrBitField, StrByteField
from ..objs import Coach, Player, Scout


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
    version_magic: bytes

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
    return_days: IntBitField
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
    wave_type: IntBitField
    salary: IntBitField
    offer_years_passed: IntBitField
    offer_years_total: IntBitField
    test: IntBitField = IntBitField(0, 0, 0)
    un: list[int]
    kan: IntBitField
    moti: IntBitField
    power: IntBitField
    super_sub: IntBitField
    wild_type: IntBitField
    weak_type: IntBitField
    tired_type: IntBitField
    pop: IntBitField
    comp_money: IntBitField
    comp_discord: IntBitField
    comp_staff: IntBitField
    comp_usage: IntBitField
    comp_result: IntBitField
    comp_status: IntBitField
    comp_euipment: IntBitField
    tired: IntBitField
    status: IntBitField
    condition: IntBitField
    explosion_exp: IntBitField
    explosion_level: IntBitField
    explo_countdown: IntBitField
    explo_pending_reason: IntBitField
    explo_final_reason: IntBitField

    def __init__(self, index: int):
        self.index = index
        self.abilities = []
        self.un = []

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
            comp=[
                self.comp_money.value,
                self.comp_discord.value,
                self.comp_staff.value,
                self.comp_usage.value,
                self.comp_result.value,
                self.comp_status.value,
                self.comp_euipment.value,
            ],
            tired=self.tired.value,
            status=self.status.value,
            condition=self.condition.value,
            explosion_exp=self.explosion_exp.value,
            explosion_level=self.explosion_level.value,
            explo_countdown=self.explo_countdown.value,
            explo_pending_reason=self.explo_pending_reason.value,
            explo_final_reason=self.explo_final_reason.value,
        )


class MyTeam:
    english_name: StrBitField
    oilis_english_name: StrBitField
    players: list[MyPlayer]
    youth_players: list[MyPlayer]
    my_scouts: list["MyScout"]
    master_coach: "MyCoach"
    my_coaches: list["MyCoach"]
    scout_candidates: list["MyScout"]
    coach_candidates: list["MyCoach"]
    album_players: list[IntBitField]
    transfer_players: list["OtherPlayer"]
    free_players: list["OtherPlayer"]
    rookie_players: list["OtherPlayer"]
    team_status: IntBitField
    my_sponsors: list["MySponsor"]
    national_team_players: list[MyPlayer]
    national_team_coach: "MyCoach"


@dataclass
class OtherPlayer:
    id: IntBitField
    age: IntBitField
    ability_graph: IntBitField | None = None
    number: IntBitField | None = None

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
    id: IntBitField
    friendly: IntBitField
    unknown1: IntBitField
    unknown2: IntBitField
    players: list[OtherPlayer]


@dataclass
class MyScout:
    id: IntBitField
    age: IntBitField
    offer_years: IntBitField
    born: IntBitField | None = None
    saved_name: StrBitField | None = None
    rank: IntBitField | None = None
    abilities: list[IntBitField] | None = None
    contract_years: IntBitField | None = None
    salary: IntBitField | None = None
    area1: IntBitField | None = None
    area2: IntBitField | None = None

    def to_dto(self) -> ScoutDto:
        abilities = [a.value for a in self.abilities] if self.abilities else []
        return ScoutDto(
            id=self.id.value,
            name=self.saved_name.value if self.saved_name else "",
            born=self.born.value if self.born else None,
            age=self.age.value,
            contract_years=self.contract_years.value if self.contract_years else 0,
            offer_years=self.offer_years.value,
            salary_high=self.salary.value * 100 // 10000 if self.salary else 0,
            salary_low=self.salary.value * 100 % 10000 if self.salary else 0,
            rank=self.rank.value if self.rank else -1,
            abilities=abilities,
            nati1=self.area1.value if self.area1 else None,
            nati2=self.area2.value if self.area2 else None,
        )

    def to_dto_with_name(self, id: int) -> ScoutDto:
        return ScoutDto(
            id=self.id.value,
            name=Scout.name(id),
            age=self.age.value,
            offer_years=self.offer_years.value,
            rank=-1,
            abilities=[],
        )


@dataclass
class MyCoach:
    id: IntBitField
    age: IntBitField
    offer_years: IntBitField
    saved_name: StrBitField | None = None
    rank: IntBitField | None = None
    abilities: list[IntBitField] | None = None
    contract_years: IntBitField | None = None
    salary: IntBitField | None = None
    sp_prac1: IntBitField | None = None
    sp_prac2: IntBitField | None = None
    coach_type: IntBitField | None = None
    born: IntBitField | None = None
    activate_plan: IntBitField | None = None
    training_plan: IntBitField | None = None
    training_strength: IntBitField | None = None
    styles: list[IntBitField] | None = None

    def to_dto(self) -> CoachDto:
        abilities = [a.value for a in self.abilities] if self.abilities else []
        styles = [a.value for a in self.styles] if self.styles else []
        return CoachDto(
            id=self.id.value,
            name=self.saved_name.value if self.saved_name else "",
            age=self.age.value,
            contract_years=self.contract_years.value if self.contract_years else 0,
            offer_years=self.offer_years.value,
            salary_high=self.salary.value * 100 // 10000 if self.salary else 0,
            salary_low=self.salary.value * 100 % 10000 if self.salary else 0,
            rank=self.rank.value if self.rank else -1,
            abilities=abilities,
            sp_prac1=self.sp_prac1.value if self.sp_prac1 else None,
            sp_prac2=self.sp_prac2.value if self.sp_prac2 else None,
            coach_type=self.coach_type.value if self.coach_type else None,
            born=self.born.value if self.born else None,
            activate_plan=self.activate_plan.value if self.activate_plan else None,
            training_plan=self.training_plan.value if self.training_plan else None,
            training_strength=self.training_strength.value if self.training_strength else None,
            styles=styles,
        )

    def to_dto_with_name(self, id: int) -> CoachDto:
        return CoachDto(
            id=self.id.value,
            name=Coach.name(id),
            age=self.age.value,
            offer_years=self.offer_years.value,
            rank=-1,
            abilities=[],
        )


@dataclass
class MySponsor:
    id: IntBitField
    contract_years: IntBitField
    offer_years: IntBitField
    amount: IntBitField

    def to_dto(self) -> SponsorDto:
        return SponsorDto(
            id=self.id.value,
            contract_years=self.contract_years.value,
            offer_years=self.offer_years.value,
            amount_high=self.amount.value * 100 // 10000,
            amount_low=self.amount.value * 100 % 10000,
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
    town_type: IntBitField

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


class Sche:
    abroad_list: list[IntBitField]
    camp_list: list[IntBitField]
