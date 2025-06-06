from dataclasses import dataclass
from pathlib import Path
from .crc_ecc import EccCaculator
from ps2mc.error import Error
from ps2mc.ps2mc import Ps2mc, Entry, Fat


class MemcardReader(Ps2mc):
    """
    Represents interfaces for interacting with PS2 memory card files.
    Provides management and operations for the `page`, `cluster`, and `fat` objects.
    See https://babyno.top/en/posts/2023/09/parsing-ps2-memcard-file-system/ for details.
    """

    def __init__(self, file_path: Path):
        """
        Initialize the Ps2mc with the path to a PS2 memory card file.

        Parameters:
        - file_path (Path): The path to the PS2 memory card file.
        """
        self.file_path = file_path
        self.offset = 0
        self.file = open(self.file_path, "rb")
        super().__init__(self.file)
        self.ecc_caculator = EccCaculator()

    def read_save_entries(self) -> list['Saka04SaveEntry']:
        save_entries: list['Saka04SaveEntry'] = list()
        root_entries = self.list_root_dir()
        for entry in [e for e in root_entries if e.name.startswith("BISLPM-65530Saka_G")]:
            sub_entries = self.lookup_entry_by_name(entry.name)
            for sub_entry in sub_entries:
                if sub_entry.is_file():
                    if sub_entry.name == entry.name:
                        main_save_entry = self.read_data_cluster(sub_entry)
                    if sub_entry.name == 'head.dat':
                        save_head_entry = self.read_data_cluster(sub_entry)
                    if sub_entry.name == 'icon.sys':
                        sys_icon_entry = self.read_data_cluster(sub_entry)
            save_entries.append(Saka04SaveEntry(entry.name, main_save_entry, save_head_entry, sys_icon_entry))
        return save_entries

    def write_save_entry(self, save_entry: 'Saka04SaveEntry', main_bytes: bytes, head_bytes: bytes = None):
        self.offset = 0
        try:
            self.file = open(self.file_path, "r+b")
            mc_entries = self.lookup_entry_by_name(save_entry.name)
            if mc_entries:
                main_entry = [f for f in mc_entries if f.name == save_entry.name][0]
                self.write_data_cluster(main_entry, main_bytes)
                if head_bytes and len(head_bytes) > 0:
                    head_entry = [f for f in mc_entries if f.name == 'head.dat'][0]
                    self.write_data_cluster(head_entry, head_bytes)
        finally:
            self.close()

    def read_bytes(self, size: int) -> bytes:
        self.file.seek(self.offset)
        return self.file.read(size)

    def write_bytes(self, data: bytes):
        self.file.seek(self.offset)
        return self.file.write(data)

    def close(self):
        if self.file:
            self.file.close()

    def write_page(self, n: int, data: bytes):
        end = min(self.page_size, len(data))
        self.offset = self.raw_page_size * n
        self.write_bytes(data[:end])
        if self.spare_size != 0:
            ecc_bytes = bytearray()
            for i in range(self.page_size // 128):
                self.file.seek(self.offset + i * 128)
                ecc_bytes.extend(self.ecc_caculator.calc(self.file.read(128)))
            ecc_bytes.extend(b"\0" * (self.spare_size - len(ecc_bytes)))
            self.offset += self.page_size
            self.write_bytes(ecc_bytes)

    def write_cluster(self, n: int, data: bytes):
        page_index = n * self.pages_per_cluster
        for i in range(self.pages_per_cluster):
            start = i * self.page_size
            self.write_page(page_index + i, data[start:])

    def write_data_cluster(self, entry: Entry, data: bytes):
        chain_start = entry.cluster
        bytes_write = 0
        while chain_start != Fat.CHAIN_END:
            to_write = min(entry.length - bytes_write, self.cluster_size)
            self.write_cluster(chain_start + self.alloc_offset, data[bytes_write: bytes_write + to_write])
            bytes_write += to_write
            chain_start = self.get_fat_value(chain_start)

    def list_root_dir(self) -> list[Entry]:
        """
        List entries in the root directory of the memory card.

        Returns:
        List: A list of entries in the root directory.
        """
        return [e for e in self.entries_in_root if e.is_exists()]

    def lookup_entry(self, entry) -> list[Entry]:
        """
        Look up sub-entries for a given entry.

        Parameters:
        - entry: The entry for which sub-entries need to be looked up.

        Returns:
        List: A list of sub-entries.
        """
        return self.find_sub_entries(entry)

    def lookup_entry_by_name(self, name: str) -> list[Entry]:
        """
        Look up entries based on the name of a game.

        Parameters:
        - name (str): The name of the game.

        Returns:
        List: A list of entries associated with the specified game name.

        Raises:
        - Error: If the specified game name cannot be found.
        """
        filters = [
            e for e in self.entries_in_root if e.name == name and e.is_dir()
        ]
        if filters:
            return self.lookup_entry(filters[0])
        raise Error(f"can't find game {name}")

@dataclass
class Saka04SaveEntry:
    name: str
    main_save_entry: bytes
    save_head_entry: bytes
    sys_icon_entry: bytes
