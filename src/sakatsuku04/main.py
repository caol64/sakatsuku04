import atexit
import platform
import socket
import subprocess
import sys
import time

import bottle
import webview

from .data_reader import DataReader
from .dtos import ClubDto, MyPlayerDto, SearchDto, TownDto
from .savereader.readers import SaveDataReader
from .pcsx2reader.readers import Pcsx2DataReader
from .utils import get_resource_path


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

    def fetch_my_town(self) -> dict:
        return self.data_raader.read_town().model_dump(by_alias=True)

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
