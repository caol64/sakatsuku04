from typing import Protocol

from .dtos import ClubDto, MyPlayerDto, OtherTeamPlayerDto


class DataReader(Protocol):

    def games(self) -> list[str]:
        ...

    def select_game(self, game: str):
        ...

    def read_club(self) -> ClubDto:
        ...

    def read_myteam(self) -> list[MyPlayerDto]:
        ...

    def read_other_team_players(self, team_index: int) -> list[OtherTeamPlayerDto]:
        ...

    def read_other_team_friendly(self, team_index: int) -> int:
        ...

    def read_myplayer(self, id: int) -> MyPlayerDto:
        ...

    def save_club(self, data: ClubDto) -> bool:
        ...

    def save_player(self, data: MyPlayerDto) -> bool:
        ...

    def save_other_team_friendly(self, team_index: int, friendly: int) -> bool:
        ...

    def reset(self): ...

    def is_cn(self) -> bool: ...
