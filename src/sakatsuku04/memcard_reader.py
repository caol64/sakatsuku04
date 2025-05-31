from dataclasses import dataclass
from pathlib import Path
import struct

import numpy as np

from . import utils
from .crc_ecc import EccCaculator
from .error import Error


class MemcardReader:
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
        self.file = None
        self.super_block = None
        self.raw_page_size = 0
        self.cluster_size = 0
        self.fat_per_cluster = 0
        self.fat_matrix = []
        self.root_entry = None
        self.entries_in_root = []
        self.spare_size = 0
        self.ecc_caculator = EccCaculator()

    def load(self):
        self.file = open(self.file_path, "rb")
        self.super_block = self.read_super_block()
        self.spare_size = (self.super_block.page_len // 128) * 4
        self.raw_page_size = self.super_block.page_len + self.spare_size
        self.cluster_size = self.super_block.page_len * self.super_block.pages_per_cluster
        self.fat_per_cluster = self.cluster_size // 4
        self.fat_matrix = self.__build_fat_matrix()
        self.root_entry = self.get_root_entry()
        self.entries_in_root = self.find_sub_entries(self.root_entry)

    def read_super_block(self) -> 'SuperBlock':
        byte_val = self.read_bytes(SuperBlock.SIZE)
        return SuperBlock(byte_val)

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

    def read_page(self, n: int) -> bytes:
        """
        Read the byte data of a page from the memory card.

        Parameters:
        - n (int): Page number.

        Returns:
            bytes: Data read from the specified page.
        """
        self.offset = self.raw_page_size * n
        return self.read_bytes(self.super_block.page_len)

    def write_page(self, n: int, data: bytes):
        end = min(self.super_block.page_len, len(data))
        self.offset = self.raw_page_size * n
        self.write_bytes(data[:end])
        if self.spare_size != 0:
            ecc_bytes = bytearray()
            for i in range(self.super_block.page_len // 128):
                self.file.seek(self.offset + i * 128)
                ecc_bytes.extend(self.ecc_caculator.calc(self.file.read(128)))
            ecc_bytes.extend(b"\0" * (self.spare_size - len(ecc_bytes)))
            self.offset += self.super_block.page_len
            self.write_bytes(ecc_bytes)

    def read_cluster(self, n: int) -> bytes:
        """
        Read the byte data of a cluster from the memory card.

        Parameters:
        - n (int): Cluster number.

        Returns:
            bytes: Data read from the specified cluster.
        """
        page_index = n * self.super_block.pages_per_cluster
        byte_buffer = bytearray()
        for i in range(self.super_block.pages_per_cluster):
            byte_buffer += self.read_page(page_index + i)
        return bytes(byte_buffer)

    def write_cluster(self, n: int, data: bytes):
        page_index = n * self.super_block.pages_per_cluster
        for i in range(self.super_block.pages_per_cluster):
            start = i * self.super_block.page_len
            self.write_page(page_index + i, data[start:])

    def get_fat_value(self, n: int) -> int:
        """
        Get the file allocation table (FAT) value for a specific cluster.

        Parameters:
        - n (int): Cluster number.

        Returns:
            int: FAT value for the specified cluster.
        """
        value = self.fat_matrix[
            (n // self.fat_per_cluster) % self.fat_per_cluster, n % self.fat_per_cluster
        ]
        return value ^ Fat.ALLOCATED_BIT if value & Fat.ALLOCATED_BIT > 0 else value

    def get_root_entry(self) -> 'Entry':
        """
        Get the root directory entry.

        Returns:
        Entry: Root directory entry.
        """
        entries = self.read_entry_cluster(self.super_block.rootdir_cluster)
        return entries[0].unpack()

    def read_entry_cluster(self, cluster_offset: int) -> list['Entry']:
        """
        Read entries from an "entry cluster."

        Parameters:
        - cluster_offset (int): Relative offset of the cluster.

        Returns:
            List[Entry]: List of entry objects.
        """
        cluster_value = self.read_cluster(cluster_offset + self.super_block.alloc_offset)
        return Entry.build(cluster_value)

    def find_sub_entries(self, parent_entry: 'Entry') -> list['Entry']:
        """
        Find sub-entries for a given parent entry.

        Parameters:
        - parent_entry (Entry): Parent entry.

        Returns:
            List[Entry]: List of sub-entries.
        """
        chain_start = parent_entry.cluster
        sub_entries: list[Entry] = []
        while chain_start != Fat.CHAIN_END:
            entries = self.read_entry_cluster(chain_start)
            for e in entries:
                if len(sub_entries) < parent_entry.length:
                    sub_entries.append(e.unpack())
            chain_start = self.get_fat_value(chain_start)
        return [x for x in sub_entries if not x.name.startswith(".")]

    def read_data_cluster(self, entry: 'Entry') -> bytes:
        """
        Read data from a chain of "data clusters" associated with a file.

        Parameters:
        - entry (Entry): Entry object representing the file.

        Returns:
            bytes: Data bytes of the file.
        """
        byte_buffer = bytearray()
        chain_start = entry.cluster
        bytes_read = 0
        while chain_start != Fat.CHAIN_END:
            to_read = min(entry.length - bytes_read, self.cluster_size)
            byte_buffer += self.read_cluster(chain_start + self.super_block.alloc_offset)[:to_read]
            bytes_read += to_read
            chain_start = self.get_fat_value(chain_start)
        return bytes(byte_buffer)

    def write_data_cluster(self, entry: 'Entry', data: bytes):
        chain_start = entry.cluster
        bytes_write = 0
        while chain_start != Fat.CHAIN_END:
            to_write = min(entry.length - bytes_write, self.cluster_size)
            self.write_cluster(chain_start + self.super_block.alloc_offset, data[bytes_write: bytes_write + to_write])
            bytes_write += to_write
            chain_start = self.get_fat_value(chain_start)

    def __build_matrix(self, cluster_list: list[int]) -> np.ndarray:
        """
        Build a matrix from a list of cluster values.

        Parameters:
        - cluster_list (List[int]): List of cluster values.

        Returns:
            np.ndarray: Matrix representation of the cluster values.
        """
        matrix = np.zeros((len(cluster_list), self.fat_per_cluster), np.uint32)
        for index, v in enumerate(cluster_list):
            cluster_value = self.read_cluster(v)
            cluster_value_unpacked = np.frombuffer(cluster_value, np.uint32)
            for index0, v0 in enumerate(cluster_value_unpacked):
                matrix[index, index0] = v0
        return matrix

    def __build_fat_matrix(self) -> np.ndarray:
        """
        Build the file allocation table (FAT) matrix.

        Returns:
            np.ndarray: Matrix representation of the FAT.
        """
        indirect_fat_matrix = self.__build_matrix(self.super_block.ifc_list)
        indirect_fat_matrix = indirect_fat_matrix.reshape(indirect_fat_matrix.size)
        indirect_fat_matrix = [x for x in indirect_fat_matrix if x != Fat.UNALLOCATED]
        fat_matrix = self.__build_matrix(indirect_fat_matrix)
        return fat_matrix

    def list_root_dir(self) -> list['Entry']:
        """
        List entries in the root directory of the memory card.

        Returns:
        List: A list of entries in the root directory.
        """
        return [e for e in self.entries_in_root if e.is_exists()]

    def lookup_entry(self, entry) -> list['Entry']:
        """
        Look up sub-entries for a given entry.

        Parameters:
        - entry: The entry for which sub-entries need to be looked up.

        Returns:
        List: A list of sub-entries.
        """
        return self.find_sub_entries(entry)

    def lookup_entry_by_name(self, name: str) -> list['Entry']:
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


    def print_all(self):
        """
        Utility method to print all entries in the memory card.
        """
        root_dirs = self.list_root_dir()
        for d in root_dirs:
            print(d.name)
            entries = self.lookup_entry(d)
            for entry in entries:
                print(f"    {entry.name}")


class SuperBlock:
    """
    The SuperBlock is a section located at the beginning of
    the PS2 memory card file with a fixed structure.
    See https://babyno.top/en/posts/2023/09/parsing-ps2-memcard-file-system/ for details.

    SuperBlock size = 340bytes
    ```
    """

    SIZE = 340
    DATA_STRUCT = struct.Struct("<28s12sHHH2xLLLL4x4x8x128s128xbbxx")
    MAGIC = b"Sony PS2 Memory Card Format "
    assert SIZE == DATA_STRUCT.size

    def __init__(self, byte_val: bytes):
        """Initialize the SuperBlock instance."""
        if len(byte_val) < SuperBlock.SIZE:
            raise Error("PCSX2 save length invalid.")
        if not byte_val.startswith(SuperBlock.MAGIC):
            raise Error("Not a valid PCSX2 save.")
        (
            self.magic,
            self.version,
            self.page_len,
            self.pages_per_cluster,
            self.pages_per_block,
            self.clusters_per_card,
            self.alloc_offset,
            self.alloc_end,
            self.rootdir_cluster,
            self.ifc_list,
            self.card_type,
            self.card_flags,
        ) = SuperBlock.DATA_STRUCT.unpack(byte_val)
        self.ifc_list = [x for x in np.frombuffer(self.ifc_list, np.uint32) if x > 0]


class Entry:
    """
    An Entry is metadata for the PS2 memory card file objects.
    See https://babyno.top/en/posts/2023/09/parsing-ps2-memcard-file-system/ for details.

    Entry size = 512bytes
    ```
    """

    MODE_PROTECTED = 0x0008
    MODE_FILE = 0x0010
    MODE_DIR = 0x0020
    MODE_HIDDEN = 0x2000
    MODE_EXISTS = 0x8000

    SIZE = 512
    DATA_STRUCT = struct.Struct("<H2xL8sL4x8s32x32s416x")
    TOD_STRUCT = struct.Struct("<xBBBBBH")  # secs, mins, hours, mday, month, year
    assert SIZE == DATA_STRUCT.size

    def __init__(self, byte_val: bytes):
        """Initialize the entry attributes."""
        self.byte_val = byte_val
        self.mode = None
        self.length = None
        self.created = None
        self.cluster = None
        self.modified = None
        self.name = None

    def unpack(self) -> 'Entry':
        """Unpack byte values into attributes after the instance is created."""
        (
            self.mode,
            self.length,
            self.created,
            self.cluster,
            self.modified,
            name,
        ) = Entry.DATA_STRUCT.unpack(self.byte_val)
        self.created = Entry.TOD_STRUCT.unpack(self.created)
        self.modified = Entry.TOD_STRUCT.unpack(self.modified)
        self.name = utils.zero_terminate(utils.decode_sjis(name))
        return self

    @staticmethod
    def build(byte_val: bytes) -> list['Entry']:
        """Build a list of Entry instances from the bytes of an entry cluster."""
        entry_count = len(byte_val) // Entry.SIZE
        entries = []
        for i in range(entry_count):
            entries.append(Entry(byte_val[i * Entry.SIZE: i * Entry.SIZE + Entry.SIZE]))
        return entries

    def is_dir(self) -> bool:
        """Check if the entry represents a directory."""
        return self.mode & (Entry.MODE_DIR | Entry.MODE_EXISTS) == (
            Entry.MODE_DIR | Entry.MODE_EXISTS
        )

    def is_file(self) -> bool:
        """Check if the entry represents a file."""
        return self.mode & (Entry.MODE_FILE | Entry.MODE_EXISTS) == (
            Entry.MODE_FILE | Entry.MODE_EXISTS
        )

    def is_exists(self) -> bool:
        """Check if the entry exists."""
        return self.mode & Entry.MODE_EXISTS > 0


class Fat:
    """
    Represents constants and operations related to the file allocation table (FAT).
    See https://babyno.top/en/posts/2023/09/parsing-ps2-memcard-file-system/ for details.

    Attributes:
    - ALLOCATED_BIT (int): Bit indicating allocated clusters.
    - UNALLOCATED (int): Value representing an unallocated cluster.
    - CHAIN_END (int): Value indicating the end of a cluster chain.
    """
    ALLOCATED_BIT = 0x80000000
    UNALLOCATED = 0xFFFFFFFF
    CHAIN_END = 0x7FFFFFFF


@dataclass
class Saka04SaveEntry:
    name: str
    main_save_entry: bytes
    save_head_entry: bytes
    sys_icon_entry: bytes
