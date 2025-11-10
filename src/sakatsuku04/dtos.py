from enum import Enum

from pydantic import BaseModel, ConfigDict, computed_field
from pydantic.alias_generators import to_camel

from . import constants
from .objs import Coach, Player, Scout
from .utils import (
    ability_to_lv,
    calc_abil_eval,
    calc_apos_eval,
    calc_def,
    calc_gk,
    calc_gp,
    calc_grow_eval,
    calc_mhex_sys,
    calc_off,
    calc_phy,
    calc_sta,
    calc_sys,
    calc_tac,
    find_badden_match,
    get_rank_to_number,
    handle_cond,
    is_album_player,
    lv_to_dot,
    mcoach_eval,
    sabil_2_apt,
)


class GameVersion(str, Enum):
    JP = "jp"
    ZH = "zh"
    ZH18 = "zh18"


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
    team_status: int = 0

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
    wave_type: int
    sp_comment: str | None
    salary_high: int
    salary_low: int
    offer_years_passed: int
    offer_years_total: int
    kan: int
    moti: int
    power: int
    super_sub: int
    wild_type: int
    weak_type: int
    tired_type: int
    pop: int
    comp: list[int]
    tired: int
    status: int
    condition: int
    explosion_exp: int
    explosion_level: int
    explo_countdown: int
    explo_pending_reason: int
    explo_final_reason: int

    @computed_field
    @property
    def is_album(self) -> bool:
        return is_album_player(self.id)

    @computed_field
    @property
    def hexagon(self) -> list[int]:
        current_abils = [f.current for f in self.abilities]
        current_max_abils = [f.current_max for f in self.abilities]
        max_abils = [f.max for f in self.abilities]
        return [
            calc_off(current_abils),
            calc_gk(current_abils) if self.pos == 0 else calc_def(current_abils),
            calc_sta(current_abils),
            calc_phy(current_abils),
            calc_sys(current_abils),
            calc_tac(current_abils),
            calc_off(current_max_abils),
            calc_gk(current_max_abils) if self.pos == 0 else calc_def(current_max_abils),
            calc_sta(current_max_abils),
            calc_phy(current_max_abils),
            calc_sys(current_max_abils),
            calc_tac(current_max_abils),
            calc_off(max_abils),
            calc_gk(max_abils) if self.pos == 0 else calc_def(max_abils),
            calc_sta(max_abils),
            calc_phy(max_abils),
            calc_sys(max_abils),
            calc_tac(max_abils),
        ]

    @computed_field
    @property
    def odc(self) -> list[int]:
        current_abils = [f.current for f in self.abilities]
        return [
            lv_to_dot(calc_off(current_abils)),
            lv_to_dot(calc_gk(current_abils) if self.pos == 0 else calc_def(current_abils)),
        ]

    @computed_field
    @property
    def abil_eval(self) -> int:
        return calc_abil_eval([r.current for r in self.abilities][0:36], self.pos)

    @computed_field
    @property
    def grow_eval(self) -> int:
        return calc_grow_eval(self.grow_type_tec, self.age)

    @computed_field
    @property
    def max_abil_eval(self) -> int:
        return calc_abil_eval([r.max for r in self.abilities][0:36], self.pos)

    @computed_field
    @property
    def apos_eval(self) -> list[int]:
        return calc_apos_eval([r.current for r in self.abilities])

    @computed_field
    @property
    def badden_players(self) -> list[str] | None:
        badden_ids = find_badden_match(self.id)
        return [Player(p).name for p in badden_ids] if badden_ids else None

    def combo_salary(self) -> int:
        return (self.salary_high * 10000 + self.salary_low) // 100

    @computed_field
    @property
    def phy_grows(self) -> list[int]:
        return list(constants.tbl_phy_grow_type[self.grow_type_phy])

    @computed_field
    @property
    def tec_grows(self) -> list[int]:
        return list(constants.tbl_tec_grow_type[self.grow_type_tec])

    @computed_field
    @property
    def sys_grows(self) -> list[int]:
        return list(constants.tbl_sys_grow_type[self.grow_type_sys])

    @computed_field
    @property
    def gp(self) -> float:
        return calc_gp([ability_to_lv(r.max) + 1 for r in self.abilities[0:36]], self.pos)


class TeamDto(BaseDto):
    index: int
    name: str
    friendly: int


class OtherTeamPlayerDto(BaseDto):
    id: int
    age: int
    ability_graph: int | None = None
    number: int
    name: str
    rank: int
    pos: int
    born: int
    cooperation_type: int
    tone_type: int
    style: int
    grow_type_phy: int
    grow_type_tec: int
    grow_type_sys: int
    team_index: int | None = None
    my_album_players: list[int] | None = None

    @computed_field
    @property
    def album_type(self) -> int:
        if not is_album_player(self.id) or not self.my_album_players:
            return 0
        convert_ids = [constants.album_players[f] for f in self.my_album_players]
        return 1 if self.id in convert_ids else 2

    @computed_field
    @property
    def scouts(self) -> list[str]:
        scouts_ids = constants.scout_excl_reversed.get(self.id)
        if scouts_ids:
            return [Scout.name(f) for f in scouts_ids]
        return []

    @computed_field
    @property
    def bring_abroads(self) -> list[int]:
        abr_dict = abroad_player_dict()
        camp_dict = camp_player_dict()
        abroad_ids = []
        if self.id in abr_dict:
            abroad_ids.append(abr_dict[self.id])
        if self.id in camp_dict:
            abroad_ids.append(camp_dict[self.id] + 1000)
        return abroad_ids


class SearchDto(BaseDto):
    name: str | None = None
    pos: int | None = None
    age: int | None = None
    country: int | None = None
    rank: int | None = None
    tone: int | None = None
    cooperation: int | None = None
    team_id: int | None = None
    style: int | None = None
    scout_action: int | None = None


class TownDto(BaseDto):
    living: int
    economy: int
    sports: int
    env: int
    population: int
    price: int
    traffic_level: int
    soccer_pop: int
    soccer_level: int
    town_type: int


class ScoutDto(BaseDto):
    id: int
    name: str
    age: int
    offer_years: int
    rank: int
    born: int | None = None
    contract_years: int | None = None
    salary_high: int | None = None
    salary_low: int | None = None
    abilities: list[int] = []
    exclusive_players: list[SearchDto] | None = None
    simi_exclusive_players: list[SearchDto] | None = None
    nati1: int | None = None
    nati2: int | None = None

    @computed_field
    @property
    def has_exclusive(self) -> bool:
        excls = constants.scout_excl_tbl.get(self.id, [])
        simi_excls = constants.scout_simi_excl_tbl.get(self.id, [])
        return len(excls) > 0 or len(simi_excls) > 0

    @computed_field
    @property
    def hexagon(self) -> list[int]:
        if len(self.abilities) == 0:
            return []
        return [
            (self.abilities[2] + self.abilities[4]) // 2,
            (self.abilities[3] + self.abilities[4] + self.abilities[5]) // 3,
            (self.abilities[1] + self.abilities[3]) // 2,
            (self.abilities[1] + self.abilities[2]) // 2,
        ]

    @computed_field
    @property
    def apos_eval(self) -> list[int]:
        if len(self.abilities) == 0:
            return []
        return [sabil_2_apt(self.abilities[constants.epos_to_pos[constants.apos_to_epos[i]] + 0x11]) for i in range(11)]

    @computed_field
    @property
    def eval(self) -> str:
        plus = 2
        if constants.scout_excl_tbl.get(self.id) is not None:
            plus = 0
        comment = Scout.scout_comments_list()[get_rank_to_number(self.rank) * 8 + plus]
        return comment

class CoachDto(BaseDto):
    id: int
    name: str
    age: int
    offer_years: int
    rank: int
    born: int | None = None
    contract_years: int | None = None
    salary_high: int | None = None
    salary_low: int | None = None
    abilities: list[int] = []
    enabled_abr_ids: list[int] = []
    enabled_camp_ids: list[int] = []
    sp_prac1: int | None = None
    sp_prac2: int | None = None
    coach_type: int | None = None
    activate_plan: int | None = None
    training_plan: int | None = None
    training_strength: int | None = None
    styles: list[int] | None = None

    @computed_field
    @property
    def bring_abroads(self) -> list["AbrStatusDto"]:
        if self.id < 20000 or (len(self.enabled_abr_ids) == 0 and len(self.enabled_camp_ids) == 0):
            return []
        abr_dict = abroad_coach_dict()
        camp_dict = camp_coach_dict()
        id = self.id - 20000
        abroad_ids = []
        if id in abr_dict:
            abroad_ids.append(AbrStatusDto(id=abr_dict[id], type=0, is_enabled=abr_dict[id] in self.enabled_abr_ids))
        if id in camp_dict:
            abroad_ids.append(AbrStatusDto(id=camp_dict[id], type=1, is_enabled=camp_dict[id] in self.enabled_camp_ids))
        return abroad_ids

    @computed_field
    @property
    def is_bring_abroad(self) -> bool:
        abr_dict = abroad_coach_dict()
        camp_dict = camp_coach_dict()
        id = self.id - 20000
        return id in abr_dict or id in camp_dict

    @computed_field
    @property
    def sp_skill(self) -> int | None:
        return constants.mcoach_skill.get(self.id - 20000)

    @computed_field
    @property
    def hexagon(self) -> list[int]:
        if len(self.abilities) == 0:
            return []
        tac_sum = self.abilities[25] + self.abilities[26] + self.abilities[27]
        tac_max = max([self.abilities[25], self.abilities[26], self.abilities[27]])
        tac_avg = (tac_sum - tac_max) // 27
        return [
            self.abilities[10],
            self.abilities[11],
            ((self.abilities[28] + self.abilities[29]) * 250 + (tac_max * 6 + tac_avg * 4) * 50) // 1000,
            calc_mhex_sys(self.abilities),
            (self.abilities[1] + self.abilities[2] + self.abilities[3]) // 3,
            (self.abilities[0] + self.abilities[2]) // 2,
        ]

    @computed_field
    @property
    def eval(self) -> str:
        if len(self.abilities) == 0:
            return ""
        rank = get_rank_to_number(self.rank)
        skill = constants.mcoach_skill.get(self.id - 20000)
        if skill is not None:
            return Coach.mcoach_comments_list()[rank * 10 + skill]
        eval_tuple = mcoach_eval(self.abilities)
        index = constants.mcoach_eval_rank_abil_mapping.get(rank)[eval_tuple[1]][eval_tuple[0]]
        comment = Coach.mcoach_comments_list()[index - 700]
        return comment


class AbroadCond(BaseDto):
    id: int
    cond: list[str | int] | None


class AbroadDto(BaseDto):
    id: int
    is_enabled: bool | None = None
    cond: AbroadCond | None = None
    abr_up: list[int] | None = None
    abr_uprate: list[int] | None = None
    abr_days: int = 0

    @classmethod
    def get_abr_camp_teams(cls, type: int) -> list["AbroadDto"]:
        results = []
        for item in constants.abr_camp_base[type]:
            dto = AbroadDto(id=item[0])
            results.append(dto)
        return results

    @classmethod
    def get_abr_teams(cls) -> list["AbroadDto"]:
        results = []
        for item in constants.abr_base:
            dto = AbroadDto(id=item[0])
            results.append(dto)
        return results

    @classmethod
    def get_camp_teams(cls) -> list["AbroadDto"]:
        results = []
        for item in constants.camp_base:
            dto = AbroadDto(id=item[0])
            results.append(dto)
        return results

    @classmethod
    def get_abr_camp_dto(cls, index: int, type: int) -> "AbroadDto":
        item = constants.abr_camp_base[type][index]
        dto = AbroadDto(id=item[0])
        dto.abr_up = list(constants.abr_camp_up[type][index])
        dto.abr_uprate = list(constants.abr_camp_uprate[type][index])
        dto.abr_days = item[3]
        cond_id = item[1] >> 4
        cond_val = handle_cond(list(item[4:14]))

        match cond_id:
            case 1 | 4:
                dto.cond = AbroadCond(id=cond_id, cond=[])
            case 5:
                dto.cond = AbroadCond(id=cond_id, cond=[Player(f).name for f in cond_val])
            case 6:
                dto.cond = AbroadCond(id=cond_id, cond=[Coach.name(f + 20000) for f in cond_val])
            case 7 | 3 | 2:
                dto.cond = AbroadCond(id=cond_id, cond=cond_val)
        return dto


class BPlayerDto(BaseDto):
    id: int = 0
    name: str
    born: int
    pos: int
    age: int
    rank: int
    tone_type: int
    cooperation_type: int
    wave_type: int
    grow_type_phy: int
    grow_type_tec: int
    grow_type_sys: int
    abilities: list[int]
    abilities_base: list[int] | None = None
    height: int
    style: int
    super_sub: int
    wild_type: int
    weak_type: int
    tired_type: int
    pop: int
    desire: int
    pride: int
    ambition: int
    patient: int
    persistence: int
    foot: int
    unlock_year: int
    signing_difficulty: int

    @computed_field
    @property
    def abil_eval(self) -> int:
        return calc_abil_eval(list(self.abilities)[0:36], self.pos)

    @computed_field
    @property
    def hexagon(self) -> list[int]:
        return [
            calc_off(self.abilities),
            calc_gk(self.abilities) if self.pos == 0 else calc_def(self.abilities),
            calc_sta(self.abilities),
            calc_phy(self.abilities),
            calc_sys(self.abilities),
            calc_tac(self.abilities),
        ]

    @computed_field
    @property
    def odc(self) -> list[int]:
        return [
            lv_to_dot(calc_off(self.abilities)),
            lv_to_dot(calc_gk(self.abilities) if self.pos == 0 else calc_def(self.abilities)),
        ]

    @computed_field
    @property
    def apos_eval(self) -> list[int]:
        return calc_apos_eval(self.abilities)

    @computed_field
    @property
    def badden_players(self) -> list[str] | None:
        badden_ids = find_badden_match(self.id)
        return [Player(p).name for p in badden_ids] if badden_ids else None

    @computed_field
    @property
    def phy_grows(self) -> list[int]:
        return list(constants.tbl_phy_grow_type[self.grow_type_phy])

    @computed_field
    @property
    def tec_grows(self) -> list[int]:
        return list(constants.tbl_tec_grow_type[self.grow_type_tec])

    @computed_field
    @property
    def sys_grows(self) -> list[int]:
        return list(constants.tbl_sys_grow_type[self.grow_type_sys])

    @computed_field
    @property
    def sp_comment(self) -> str:
        player = Player(self.id)
        sp_comment = player.sp_comment
        if sp_comment:
            return sp_comment
        index = self.rank // 2 * 8 if self.rank < 10 else 32
        if self.age < constants.bplayer_eval_age_threshold[self.grow_type_tec]:
            return Player.player_eval_list()[index]
        return Player.player_eval_list()[index + 40]

    @computed_field
    @property
    def grow_eval(self) -> int:
        if Player(self.id).sp_comment:
            return 0
        return calc_grow_eval(self.grow_type_tec, self.age)

    @computed_field
    @property
    def gp(self) -> float:
        return calc_gp(list(self.abilities_base[0:36]), self.pos) if self.abilities_base else 0


class SimpleBPlayerDto(BaseDto):
    id: int
    name: str
    pos: int

    @computed_field
    @property
    def is_album(self) -> bool:
        return is_album_player(self.id)

    @computed_field
    @property
    def scouts(self) -> list[str]:
        scouts_ids = constants.scout_excl_reversed.get(self.id)
        if scouts_ids:
            return [Scout.name(f) for f in scouts_ids]
        return []

    @computed_field
    @property
    def bring_abroads(self) -> list[int]:
        abr_dict = abroad_player_dict()
        camp_dict = camp_player_dict()
        abroad_ids = []
        if self.id in abr_dict:
            abroad_ids.append(abr_dict[self.id])
        if self.id in camp_dict:
            abroad_ids.append(camp_dict[self.id] + 1000)
        return abroad_ids


class SimpleBScoutDto(BaseDto):
    id: int
    name: str

    @computed_field
    @property
    def has_exclusive(self) -> bool:
        excls = constants.scout_excl_tbl.get(self.id, [])
        simi_excls = constants.scout_simi_excl_tbl.get(self.id, [])
        return len(excls) > 0 or len(simi_excls) > 0


class SimpleBCoachDto(BaseDto):
    id: int
    name: str

    @computed_field
    @property
    def sp_skill(self) -> int | None:
        return constants.mcoach_skill.get(self.id - 20000)

    @computed_field
    @property
    def is_bring_abroad(self) -> bool:
        abr_dict = abroad_coach_dict()
        camp_dict = camp_coach_dict()
        id = self.id - 20000
        return id in abr_dict or id in camp_dict


class BScoutDto(BaseDto):
    id: int = 0
    name: str
    born: int
    abilities: list[int]
    nati1: int
    nati2: int
    age: int
    rank: int
    salary_high: int
    salary_low: int
    signing_difficulty: int
    ambition: int
    persistence: int

    @computed_field
    @property
    def hexagon(self) -> list[int]:
        return [
            (self.abilities[2] + self.abilities[4]) // 2,
            (self.abilities[3] + self.abilities[4] + self.abilities[5]) // 3,
            (self.abilities[1] + self.abilities[3]) // 2,
            (self.abilities[1] + self.abilities[2]) // 2,
        ]

    @computed_field
    @property
    def apos_eval(self) -> list[int]:
        return [sabil_2_apt(self.abilities[constants.epos_to_pos[constants.apos_to_epos[i]] + 0x11]) for i in range(11)]

    @computed_field
    @property
    def exclusive_players(self) -> list[str]:
        return [Player(f).name for f in constants.scout_excl_tbl.get(self.id, [])]

    @computed_field
    @property
    def simi_exclusive_players(self) -> list[str]:
        return [Player(f).name for f in constants.scout_simi_excl_tbl.get(self.id, [])]

    @computed_field
    @property
    def eval(self) -> str:
        plus = 2
        if constants.scout_excl_tbl.get(self.id) is not None:
            plus = 0
        comment = Scout.scout_comments_list()[get_rank_to_number(self.rank) * 8 + plus]
        return comment


class BCoachDto(BaseDto):
    id: int = 0
    name: str
    born: int
    age: int
    abilities: list[int]
    rank: int
    salary_high: int
    salary_low: int
    signing_difficulty: int
    styles: list[int]
    coach_type: int
    desire: int
    ambition: int
    persistence: int
    activate_plan: int
    training_plan: int
    training_strength: int
    ac_sp_practice1: int
    ac_sp_practice2: int

    @computed_field
    @property
    def hexagon(self) -> list[int]:
        tac_sum = self.abilities[25] + self.abilities[26] + self.abilities[27]
        tac_max = max([self.abilities[25], self.abilities[26], self.abilities[27]])
        tac_avg = (tac_sum - tac_max) // 27
        return [
            self.abilities[10],
            self.abilities[11],
            ((self.abilities[28] + self.abilities[29]) * 250 + (tac_max * 6 + tac_avg * 4) * 50) // 1000,
            calc_mhex_sys(self.abilities),
            (self.abilities[1] + self.abilities[2] + self.abilities[3]) // 3,
            (self.abilities[0] + self.abilities[2]) // 2,
        ]

    @computed_field
    @property
    def eval(self) -> str:
        rank = get_rank_to_number(self.rank)
        skill = constants.mcoach_skill.get(self.id - 20000)
        if skill is not None:
            return Coach.mcoach_comments_list()[rank * 10 + skill]
        eval_tuple = mcoach_eval(self.abilities)
        index = constants.mcoach_eval_rank_abil_mapping.get(rank)[eval_tuple[1]][eval_tuple[0]]
        comment = Coach.mcoach_comments_list()[index - 700]
        return comment

    @computed_field
    @property
    def sp_skill(self) -> int | None:
        return constants.mcoach_skill.get(self.id - 20000)

    @computed_field
    @property
    def coach_type_cnv(self) -> int:
        return constants.coach_mapping[self.coach_type]

    @computed_field
    @property
    def bring_abroads(self) -> list["AbrStatusDto"]:
        abr_dict = abroad_coach_dict()
        camp_dict = camp_coach_dict()
        id = self.id - 20000
        abroad_ids = []
        if id in abr_dict:
            abroad_ids.append(AbrStatusDto(id=abr_dict[id], type=0, is_enabled=False))
        if id in camp_dict:
            abroad_ids.append(AbrStatusDto(id=camp_dict[id], type=1, is_enabled=False))
        return abroad_ids


class AbrStatusDto(BaseDto):
    id: int
    type: int
    is_enabled: bool = False


class SponsorCombo(BaseDto):
    parent_id: int
    subsidiary_ids: list[int]
    type: int

class SponsorDto(BaseDto):
    id: int
    contract_years: int
    offer_years: int
    amount_high: int
    amount_low: int
    enabled_abr_ids: list[int] = []
    enabled_camp_ids: list[int] = []

    @computed_field
    @property
    def bring_abroads(self) -> list[AbrStatusDto]:
        abr_dict = abroad_sponsor_dict()
        camp_dict = camp_sponsor_dict()
        abroad_ids = []
        if self.id in abr_dict:
            abroad_ids.append(AbrStatusDto(id=abr_dict[self.id], type=0, is_enabled=abr_dict[self.id] in self.enabled_abr_ids))
        if self.id in camp_dict:
            abroad_ids.append(AbrStatusDto(id=camp_dict[self.id], type=1, is_enabled=camp_dict[self.id] in self.enabled_camp_ids))
        return abroad_ids

    @computed_field
    @property
    def combo(self) -> list[SponsorCombo]:
        result = []
        for k, v in constants.sponsor_combo.items():
            if self.id == k or self.id in v[1]:
                result.append(SponsorCombo(parent_id=k, subsidiary_ids=v[1], type=v[0]))
        return result


_abroad_sponsor_dict: dict | None = None
_abroad_coach_dict: dict | None = None
_abroad_player_dict: dict | None = None
_camp_sponsor_dict: dict | None = None
_camp_coach_dict: dict | None = None
_camp_player_dict: dict | None = None

def _build_abroad_dict(cache: dict | None, base_data: list[tuple], cond_type: int) -> dict[int, int]:
    if cache is None:
        cache = {}
        for item in base_data:
            id = item[0]
            cond_id = item[1] >> 4
            if cond_id == cond_type:
                cond_val = handle_cond(list(item[4:14]))
                for cv in cond_val:
                    cache[cv] = id
    return cache

def abroad_coach_dict() -> dict[int, int]:
    global _abroad_coach_dict
    return _build_abroad_dict(_abroad_coach_dict, constants.abr_base, 6)


def camp_coach_dict() -> dict[int, int]:
    global _camp_coach_dict
    return _build_abroad_dict(_camp_coach_dict, constants.camp_base, 6)


def abroad_sponsor_dict() -> dict[int, int]:
    global _abroad_sponsor_dict
    return _build_abroad_dict(_abroad_sponsor_dict, constants.abr_base, 2)


def camp_sponsor_dict() -> dict[int, int]:
    global _camp_sponsor_dict
    return _build_abroad_dict(_camp_sponsor_dict, constants.camp_base, 2)


def abroad_player_dict() -> dict[int, int]:
    global _abroad_player_dict
    return _build_abroad_dict(_abroad_player_dict, constants.abr_base, 5)


def camp_player_dict() -> dict[int, int]:
    global _camp_player_dict
    return _build_abroad_dict(_camp_player_dict, constants.camp_base, 5)
