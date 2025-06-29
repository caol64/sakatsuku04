import sys
import subprocess
import socket
import time
import webview
import atexit
import bottle

from .utils import get_resource_path, team_group_index
from .bit_stream import InputBitStream, OutputBitStream
from .readers import ClubReader, OtherTeamReader, TeamReader
from .models import Club, MyTeam, OtherTeam, Saka04SaveEntry, IntBitField, StrBitField
from .dtos import ClubDto, TeamDto, TeamsWithRegionDto
from .save_reader import SaveHeadReader, SaveReader
from .memcard_reader import MemcardReader


class MainApp:
    def __init__(self, web_root: str = "./webview/build", dev_port: int = 1420):
        self.web_root = web_root
        self.dev_port = dev_port
        self.bottle_app: bottle.Bottle = None
        self.mc_reader: MemcardReader = None
        self.save_entries: dict[str, Saka04SaveEntry] = None
        self.save_reader: SaveReader = None
        self.in_bit_stream: InputBitStream = None
        self.out_bit_stream: OutputBitStream = None
        self.club: Club = None
        self.my_team: MyTeam = None
        self.other_teams: list[OtherTeam] = None
        self.window_size = (1024, 768)
        self.app_name = ""
        self.app_version = 0

    def get_project_info(self, pyproject_path="pyproject.toml") -> tuple:
        import tomllib
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["project"]["name"], data["project"]["version"]

    def run_dev(self):
        self.app_name, self.app_version = self.get_project_info()
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

        window = webview.create_window(self.app_name, url=f"http://localhost:{self.dev_port}", width=self.window_size[0], height=self.window_size[1], min_size=self.window_size)
        self._expose(window)
        webview.start(debug=True)

    def run_prod(self):
        self.app_name, self.app_version = self.get_project_info()
        self._run_prod(False)

    def run_release(self):
        self.app_name, self.app_version = self.get_project_info(get_resource_path("pyproject.toml").resolve())
        self._run_prod(True)

    def _run_prod(self, is_release: bool):
        self.bottle_app = self._create_bottle_app(is_release)
        window = webview.create_window(self.app_name, url=self.bottle_app, width=self.window_size[0], height=self.window_size[1], min_size=self.window_size)
        self._expose(window)
        webview.start()

    def _expose(self, window: webview.Window):
        window.expose(
            self.pick_file,
            self.reset,
            self.fetch_save_data,
            self.save_club_data,
            self.fetch_other_teams,
            self.fetch_team_player,
            self.fetch_my_team,
        )

    def _wait_for_port(self, host: str, port: int, timeout: int = 30):
        """Wait until a port becomes available within a timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.create_connection((host, port), timeout=1):
                    return True
            except OSError:
                time.sleep(0.1)
        raise TimeoutError(f"Port {port} on {host} not available after {timeout} seconds")

    def _start_vite(self):
        """Start Vite development server"""
        return subprocess.Popen(["pnpm", "--filter", "webview", "dev"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

    def _create_bottle_app(self, is_release: bool) -> bottle.Bottle:
        app = bottle.Bottle()

        @app.route('/')
        @app.route('/<file:path>')
        def index(file=None):
            if not file:
                file = "index.html"
            bottle.response.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            bottle.response.set_header('Pragma', 'no-cache')
            bottle.response.set_header('Expires', 0)
            web_root = get_resource_path("webview/build").resolve() if is_release else self.web_root
            return bottle.static_file(file, root=web_root)

        return app

    def pick_file(self) -> list:
        file_paths = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False)
        if file_paths:
            self.mc_reader = MemcardReader(file_paths[0])
            save_entries = self.mc_reader.read_save_entries()
            self.save_entries = { item.name: item for item in save_entries }
            return [{ "name": e.name } for e in save_entries]
        else:
            return None

    def reset(self):
        self.mc_reader = None
        self.save_entries = None
        self.save_reader = None
        self.in_bit_stream = None
        self.out_bit_stream = None
        self.club = None
        self.my_team = None
        self.other_teams = None

    def fetch_save_data(self, selected_game: str) -> dict:
        save_entry = self.save_entries.get(selected_game)
        self.save_reader = SaveReader(save_entry.main_save_entry)
        self.save_reader.check_crc()
        self.save_reader.dec()
        decoded_byte_array = self.save_reader.decoded_data()
        self.in_bit_stream = InputBitStream(decoded_byte_array)
        self.out_bit_stream = OutputBitStream(decoded_byte_array)
        club_reader = ClubReader(self.in_bit_stream)
        self.club = club_reader.read()
        team_reader = TeamReader(self.in_bit_stream)
        self.my_team = team_reader.read()
        oteam_reader = OtherTeamReader(self.in_bit_stream)
        self.other_teams = oteam_reader.read()
        return self.club.to_dto().model_dump(by_alias=True)

    def save_club_data(self, data: dict, selected_game: str) -> dict:
        save_entry = self.save_entries.get(selected_game)
        club_data = ClubDto.model_validate(data)
        self.club.set_funds(club_data.fund_heigh, club_data.fund_low)
        self.club.year.value = club_data.year + 2003
        self.club.difficulty.value = club_data.difficulty
        bits_fields = list()
        bits_fields.append(self.club.funds)
        bits_fields.append(self.club.year)
        bits_fields.append(self.club.difficulty)
        head_reader = SaveHeadReader(save_entry.save_head_entry)
        head_reader.check_crc()
        head = head_reader.read()
        head.year.value = club_data.year + 2003
        head_reader.write(head.year)
        head_bytes = head_reader.build_save_bytes()
        self._save(selected_game, bits_fields, head_bytes)
        return {
            "message": "success"
        }

    def fetch_my_team(self) -> list:
        result = []
        for player in [player for player in self.my_team.sorted_players if player.id.value != 0xffff]:
            result.append(player.to_dto().model_dump(by_alias=True))
        return result

    def fetch_other_teams(self) -> list:
        group_names = sorted(team_group_index.keys(), key=lambda k: team_group_index[k])
        result = []
        for i, group_name in enumerate(group_names):
            start_index = team_group_index[group_name]
            end_index = team_group_index[group_names[i + 1]] if i + 1 < len(group_names) else len(self.other_teams)
            teams_with_region = TeamsWithRegionDto(region=group_name, teams=[])
            for team in self.other_teams[start_index:end_index]:
                teams_with_region.teams.append(TeamDto(index=team.index, name=team.name, friendly=team.friendly.value))
            result.append(teams_with_region.model_dump(by_alias=True))
        return result

    def fetch_team_player(self, team_index: int) -> list:
        team = self.other_teams[team_index]
        result = []
        for player in [player for player in team.sorted_players if player.id.value != 0xffff]:
            result.append(player.to_dto().model_dump(by_alias=True))
        return result

    def _save(self, selected_game: str, bit_fields: list[IntBitField | StrBitField], head_bytes: bytes):
        for bit_field in bit_fields:
            self.out_bit_stream.pack_bits(bit_field)
        self.save_reader.update_decode_buffer(self.out_bit_stream.input_data)
        encode_buffer = self.save_reader.enc()
        save_bin = self.save_reader.build_save_bytes(encode_buffer)
        self.mc_reader.write_save_entry(selected_game, save_bin, head_bytes)


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
