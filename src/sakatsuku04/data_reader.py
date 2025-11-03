from typing import Protocol

from .dtos import AbroadDto, ClubDto, CoachDto, MyPlayerDto, MySponsorDto, OtherTeamPlayerDto, ScoutDto, SearchDto, TownDto


class DataReader(Protocol):

    def games(self) -> list[str]:
        ...

    def select_game(self, game: str):
        ...

    def read_club(self) -> ClubDto:
        ...

    def read_myteam(self) -> list[MyPlayerDto]:
        ...

    def read_youth_team(self) -> list[MyPlayerDto]:
        ...

    def read_other_team_players(self, team_index: int) -> list[OtherTeamPlayerDto]:
        ...

    def read_other_team_friendly(self, team_index: int) -> int:
        ...

    def read_myplayer(self, id: int, team: int) -> MyPlayerDto:
        ...

    def read_scouts(self, type: int) -> list[ScoutDto]:
        ...

    def read_coaches(self, type: int) -> list[CoachDto]:
        ...

    def read_town(self) -> TownDto:
        ...

    def read_my_album_players(self) -> list[int]:
        ...

    def read_my_abroads(self, type: int) -> list[AbroadDto]:
        ...

    def read_one_abroad(self, index: int, type: int) -> AbroadDto:
        ...

    def save_club(self, data: ClubDto) -> bool:
        ...

    def save_player(self, data: MyPlayerDto, team: int) -> bool:
        ...

    def save_other_team_friendly(self, team_index: int, friendly: int) -> bool:
        ...

    def search_player(self, data: SearchDto) -> list[OtherTeamPlayerDto]:
        ...

    def save_town(self, data: TownDto) -> bool:
        ...

    def read_sponsors(self, type: int) -> list[MySponsorDto]:
        ...

    def reset(self): ...

    def game_ver(self) -> int:
        """
        0: jp
        1: cn 1.01
        2: cn 1.18
        """
        ...
