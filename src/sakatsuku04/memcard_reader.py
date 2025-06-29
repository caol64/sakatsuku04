from pathlib import Path

from .models import Saka04SaveEntry
from ps2mc import Browser


class MemcardReader():
    """
    Represents interfaces for interacting with PS2 memory card files.
    Provides management and operations for the `page`, `cluster`, and `fat` objects.
    See https://babyno.top/en/posts/2023/09/parsing-ps2-memcard-file-system/ for details.
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def read_save_entries(self) -> list[Saka04SaveEntry]:
        save_entries: list[Saka04SaveEntry] = list()
        with Browser(self.file_path) as browser:
            root_entries = browser.list_root_dir()
            for entry in [e for e in root_entries if e.name.startswith("BISLPM-65530Saka_G")]:
                sub_entries = browser.lookup_entry_by_name(entry.name)
                for sub_entry in sub_entries:
                    if sub_entry.is_file():
                        if sub_entry.name == entry.name:
                            main_save_entry = browser.ps2mc.read_data_cluster(sub_entry)
                        if sub_entry.name == 'head.dat':
                            save_head_entry = browser.ps2mc.read_data_cluster(sub_entry)
                        if sub_entry.name == 'icon.sys':
                            sys_icon_entry = browser.ps2mc.read_data_cluster(sub_entry)
                save_entries.append(Saka04SaveEntry(entry.name, main_save_entry, save_head_entry, sys_icon_entry))
            return save_entries

    def write_save_entry(self, selected_game: str, main_bytes: bytes, head_bytes: bytes = None):
        with Browser(self.file_path) as browser:
            mc_entries = browser.lookup_entry_by_name(selected_game)
            if mc_entries:
                main_entry = [f for f in mc_entries if f.name == selected_game][0]
                browser.ps2mc.write_data_cluster(main_entry, main_bytes)
                if head_bytes and len(head_bytes) > 0:
                    head_entry = [f for f in mc_entries if f.name == 'head.dat'][0]
                    browser.ps2mc.write_data_cluster(head_entry, head_bytes)
