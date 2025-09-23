import atexit
import platform
import socket
import subprocess
import sys
import time

import bottle
import webview

from .io import CnVer
from .objs import Player, Reseter, Scout, Coach
from .data_reader import DataReader
from .dtos import ClubDto, MyPlayerDto, SearchDto, SimpleBCoachDto, SimpleBScoutDto, TownDto, SimpleBPlayerDto
from .savereader.readers import SaveDataReader
from .pcsx2reader.readers import Pcsx2DataReader
from .binreader.bplayer_reader import get_player
from .binreader.bscout_reader import get_scout
from .binreader.bcoach_reader import get_coach
from .constants import exp_to_lv
from .utils import find_name_matches, get_probability_tbl_index, get_resource_path, is_jmodifiable, modify_jabil, random_get_0to1, random_get_0toi


APP_NAME = "球会04修改器"


class MainApp:
    def __init__(self, web_root: str = "./webview/build", dev_port: int = 1420):
        self.web_root = web_root
        self.dev_port = dev_port
        self.bottle_app: bottle.Bottle = None
        if platform.system() == "Darwin":
            self.window_size = (1024, 768)
        else:
            self.window_size = (1080, 830)
        self.app_name = APP_NAME
        self.app_version = ""
        self.data_raader: DataReader = None

    def get_project_info(self, pyproject_path="pyproject.toml") -> tuple:
        import tomllib

        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["project"]["name"], data["project"]["version"]

    def run_dev(self):
        _, self.app_version = self.get_project_info()
        print("🔧 Starting Vite dev server...")
        vite_process = self._start_vite()
        atexit.register(vite_process.terminate)

        try:
            self._wait_for_port("localhost", self.dev_port)
            print("✅ Vite server is ready, starting main app...")
        except TimeoutError as e:
            print(f"❌ Vite failed to start: {e}")
            vite_process.kill()
            sys.exit(1)

        window = webview.create_window(
            self.app_name,
            url=f"http://localhost:{self.dev_port}",
            width=self.window_size[0],
            height=self.window_size[1],
            min_size=self.window_size,
        )
        self._expose(window)
        webview.start(debug=True)

    def run_prod(self):
        _, self.app_version = self.get_project_info()
        self._run_prod(False)

    def run_release(self):
        _, self.app_version = self.get_project_info(
            get_resource_path("pyproject.toml").resolve()
        )
        self._run_prod(True)

    def _run_prod(self, is_release: bool):
        self.bottle_app = self._create_bottle_app(is_release)
        window = webview.create_window(
            self.app_name,
            url=self.bottle_app,
            width=self.window_size[0],
            height=self.window_size[1],
            min_size=self.window_size,
        )
        self._expose(window)
        webview.start()

    def _wait_for_port(self, host: str, port: int, timeout: int = 30):
        """Wait until a port becomes available within a timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.create_connection((host, port), timeout=1):
                    return True
            except OSError:
                time.sleep(0.1)
        raise TimeoutError(
            f"Port {port} on {host} not available after {timeout} seconds"
        )

    def _start_vite(self):
        """Start Vite development server"""
        return subprocess.Popen(
            ["pnpm", "--filter", "webview", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

    def _create_bottle_app(self, is_release: bool) -> bottle.Bottle:
        app = bottle.Bottle()

        @app.route("/")
        @app.route("/<file:path>")
        def index(file=None):
            if not file:
                file = "index.html"
            bottle.response.set_header(
                "Cache-Control", "no-cache, no-store, must-revalidate"
            )
            bottle.response.set_header("Pragma", "no-cache")
            bottle.response.set_header("Expires", 0)
            web_root = (
                get_resource_path("webview/build").resolve()
                if is_release
                else self.web_root
            )
            return bottle.static_file(file, root=web_root)

        return app

    def _expose(self, window: webview.Window):
        window.expose(
            self.get_version,
            self.pick_file,
            self.connect_pcsx2,
            self.reset,
            self.select_game,
            self.fetch_club_data,
            self.save_club_data,
            self.fetch_team_player,
            self.fetch_my_team,
            self.fetch_my_player,
            self.save_my_player,
            self.fetch_team_friendly,
            self.save_team_friendly,
            self.search_player,
            self.fetch_my_town,
            self.save_my_town,
            self.fetch_my_scouts,
            self.fetch_my_album_players,
            self.fetch_abroads,
            self.fetch_one_abroad,
            self.fetch_bplayers,
            self.get_bplayer,
            self.fetch_bscouts,
            self.fetch_bcoachs,
            self.get_bscout,
            self.get_bcoach,
        )

    def get_version(self) -> str:
        return self.app_version

    def pick_file(self) -> list:
        file_paths = webview.windows[0].create_file_dialog(
            webview.OPEN_DIALOG, allow_multiple=False
        )
        if file_paths:
            self.data_raader = SaveDataReader(file_paths[0])
            return self.data_raader.games()
        else:
            return None

    def connect_pcsx2(self) -> bool:
        self.data_raader = Pcsx2DataReader()
        return self.data_raader.check_connect()

    def reset(self):
        if self.data_raader:
            self.data_raader.reset()
        Reseter.reset()

    def select_game(self, game: str):
        self.data_raader.select_game(game)

    def fetch_club_data(self) -> dict:
        return self.data_raader.read_club().model_dump(by_alias=True)

    def save_club_data(self, data: dict) -> dict:
        club_data = ClubDto.model_validate(data)
        self.data_raader.save_club(club_data)
        return {"message": "success"}

    def fetch_my_team(self, team: int) -> list:
        if team == 0:
            return [f.model_dump(by_alias=True) for f in self.data_raader.read_myteam()]
        else:
            return [f.model_dump(by_alias=True) for f in self.data_raader.read_youth_team()]

    def fetch_team_player(self, team_index: int) -> list:
        return [f.model_dump(by_alias=True) for f in self.data_raader.read_other_team_players(team_index)]

    def fetch_team_friendly(self, team_index: int) -> int:
        return self.data_raader.read_other_team_friendly(team_index)

    def fetch_my_player(self, id: int, team: int) -> dict:
        return self.data_raader.read_myplayer(id, team).model_dump(by_alias=True)

    def fetch_my_scouts(self, type: int) -> list:
        return [f.model_dump(by_alias=True) for f in self.data_raader.read_scouts(type)]

    def fetch_my_town(self) -> dict:
        return self.data_raader.read_town().model_dump(by_alias=True)

    def fetch_my_album_players(self) -> list:
        return self.data_raader.read_my_album_players()

    def fetch_abroads(self, type: int) -> list:
        return [f.model_dump(by_alias=True) for f in self.data_raader.read_my_abroads(type)]

    def fetch_one_abroad(self, index: int, type: int) -> dict:
        return self.data_raader.read_one_abroad(index, type).model_dump(by_alias=True)

    def save_my_player(self, data: dict, team: int) -> dict:
        player_data = MyPlayerDto.model_validate(data)
        self.data_raader.save_player(player_data, team)
        return {"message": "success"}

    def save_team_friendly(self, team_index: int, friendly: int) -> dict:
        self.data_raader.save_other_team_friendly(team_index, friendly)
        return {"message": "success"}

    def search_player(self, data: dict) -> list:
        search_data = SearchDto.model_validate(data)
        if search_data.pos:
            search_data.pos -= 1
        if search_data.rank:
            search_data.rank -= 1
        if search_data.cooperation:
            search_data.cooperation -= 1
        if search_data.tone:
            search_data.tone -= 1
        return [f.model_dump(by_alias=True) for f in self.data_raader.search_player(search_data)]

    def save_my_town(self, data: dict) -> dict:
        town_data = TownDto.model_validate(data)
        self.data_raader.save_town(town_data)
        return {"message": "success"}

    def fetch_bplayers(self, page: int, search_params: dict = None) -> dict:
        CnVer.set_ver(1)
        results = []
        if not page:
            page = 1
        total = 0
        if search_params is None:
            player_count = len(Player.player_dict())
            total = (player_count + 24) // 25
            start = (page - 1) * 25
            end = min(start + 25, player_count)
            for id in range(start, end):
                p = Player(id)
                sp = SimpleBPlayerDto(id=p.id, name=p.name, pos=p.pos)
                results.append(sp.model_dump(by_alias=True))
        else:
            keyword = search_params.get("keyword")
            if keyword:
                try:
                    id = int(keyword, 16)
                except Exception:
                    id = None
                if id is not None:
                    p = Player(id)
                    if not p.name:
                        page = 1
                        total = 0
                    else:
                        sp = SimpleBPlayerDto(id=p.id, name=p.name, pos=p.pos)
                        results.append(sp.model_dump(by_alias=True))
                        page = 1
                        total = 1
                else:
                    filter_ids = find_name_matches(Player.player_dict(), keyword)
                    sorted_ids = sorted(filter_ids)
                    total = (len(sorted_ids) + 24) // 25
                    start = (page - 1) * 25
                    end = start + 25
                    page_ids = sorted_ids[start:end]
                    for id in page_ids:
                        p = Player(id)
                        sp = SimpleBPlayerDto(id=p.id, name=p.name, pos=p.pos)
                        results.append(sp.model_dump(by_alias=True))
            else:
                page = 1
                total = 0
        return {
            "page": page,
            "total": total,
            "data": results,
        }

    def get_bplayer(self, id: int, year: int = 1, age = 0, pos = None) -> dict:
        bplayer = get_player(id)
        player = Player(id)
        bplayer.name = player.name
        if age:
            bplayer.age = age
        if pos is not None and pos > -1:
            bplayer.pos = pos
        if is_jmodifiable(id):
            up_level = modify_jabil(bplayer.wave_type, year)
            if up_level > 0:
                for i in range(64):
                    bplayer.abilities[i] = min(bplayer.abilities[i] + up_level, 95)
        abilities_base = bplayer.abilities.copy()
        next_seed = id * (year - 1)
        abils = []
        for i in range(64):
            val, next_seed = random_get_0to1(next_seed)
            a = get_probability_tbl_index(bplayer.wave_type, val)
            abil_level, next_seed = random_get_0toi(next_seed, a + 2)
            ran, next_seed = random_get_0toi(next_seed, 2)
            if ran != 0:
                abil_level = -abil_level
            abil_val = min(bplayer.abilities[i] + abil_level, 100)
            abil_exp = exp_to_lv[abil_val]
            if abil_exp == 0:
                abil_exp = 1
            abils.append(abil_exp)
            abilities_base[i] = min(abilities_base[i] + abil_level, 100)
        bplayer.abilities = abils
        dto = bplayer.to_dto()
        dto.id = id
        dto.abilities_base = abilities_base
        return dto.model_dump(by_alias=True)

    def fetch_bscouts(self, page: int, search_params: dict = None) -> dict:
        CnVer.set_ver(1)
        results = []
        if not page:
            page = 1
        total = 0
        if search_params is None:
            player_count = len(Scout.scout_dict())
            total = (player_count + 24) // 25
            start = (page - 1) * 25
            end = min(start + 25, player_count)
            for i in range(start, end):
                id = i + 30000
                sp = SimpleBScoutDto(id=id, name=Scout.name(id))
                results.append(sp.model_dump(by_alias=True))
        else:
            keyword = search_params.get("keyword")
            if keyword:
                try:
                    id = int(keyword, 16)
                except Exception:
                    id = None
                if id is not None:
                    if not Scout.exsists(id):
                        page = 1
                        total = 0
                    else:
                        sp = SimpleBScoutDto(id=id, name=Scout.name(id))
                        results.append(sp.model_dump(by_alias=True))
                        page = 1
                        total = 1
                else:
                    filter_ids = find_name_matches(Scout.scout_dict(), keyword)
                    sorted_ids = sorted(filter_ids)
                    total = (len(sorted_ids) + 24) // 25
                    start = (page - 1) * 25
                    end = start + 25
                    page_ids = sorted_ids[start:end]
                    for id in page_ids:
                        sp = SimpleBScoutDto(id=id, name=Scout.name(id))
                        results.append(sp.model_dump(by_alias=True))
            else:
                page = 1
                total = 0
        return {
            "page": page,
            "total": total,
            "data": results,
        }

    def get_bscout(self, id: int) -> dict:
        if id:
            bscout = get_scout(id)
            bscout.name = Scout.name(id)
            dto = bscout.to_dto()
            dto.id = id
            return dto.model_dump(by_alias=True)
        else:
            return {}

    def fetch_bcoachs(self, page: int, search_params: dict = None) -> dict:
        CnVer.set_ver(1)
        results = []
        if not page:
            page = 1
        total = 0
        if search_params is None:
            player_count = len(Coach.coach_dict())
            total = (player_count + 24) // 25
            start = (page - 1) * 25
            end = min(start + 25, player_count)
            for i in range(start, end):
                id = i + 20000
                sp = SimpleBCoachDto(id=id, name=Coach.name(id))
                results.append(sp.model_dump(by_alias=True))
        else:
            keyword = search_params.get("keyword")
            if keyword:
                try:
                    id = int(keyword, 16)
                except Exception:
                    id = None
                if id is not None:
                    if not Coach.exsists(id):
                        page = 1
                        total = 0
                    else:
                        sp = SimpleBCoachDto(id=id, name=Coach.name(id))
                        results.append(sp.model_dump(by_alias=True))
                        page = 1
                        total = 1
                else:
                    filter_ids = find_name_matches(Coach.coach_dict(), keyword)
                    sorted_ids = sorted(filter_ids)
                    total = (len(sorted_ids) + 24) // 25
                    start = (page - 1) * 25
                    end = start + 25
                    page_ids = sorted_ids[start:end]
                    for id in page_ids:
                        sp = SimpleBCoachDto(id=id, name=Coach.name(id))
                        results.append(sp.model_dump(by_alias=True))
            else:
                page = 1
                total = 0
        return {
            "page": page,
            "total": total,
            "data": results,
        }

    def get_bcoach(self, id: int) -> dict:
        if id:
            bcoach = get_coach(id)
            bcoach.name = Coach.name(id)
            dto = bcoach.to_dto()
            dto.id = id
            return dto.model_dump(by_alias=True)
        else:
            return {}

def main():
    app = MainApp()
    env = sys.argv[1] if len(sys.argv) > 1 else "release"
    if env == "dev":
        app.run_dev()
    elif env == "prod":
        app.run_prod()
    else:
        app.run_release()


if __name__ == "__main__":
    main()
