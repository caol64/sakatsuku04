from pathlib import Path
import threading
import wx
import wx.grid
import wx.lib.agw.pygauge as PG

from .bit_stream import InputBitStream, OutputBitStream
from .error import Error
from .memcard_reader import MemcardReader, Saka04SaveEntry
from .models import CooperationType, GrowType, IntBitField, IntByteField, MyPlayer, MyTeam, OtherTeam, PlayerAbility, Position, Region, Scout, StrBitField, StrByteField, Style, ToneType
from .readers import ClubReader, OtherTeamReader, TeamReader
from .save_reader import SaveHeadReader, SaveReader
from .utils import CnVersion
from .version import APP_DISPLAY_NAME


class MemcardViewFrame(wx.Frame):
    def __init__(self, *args, file_path: Path, parent: wx.Frame, **kw):
        self.parent = parent
        self.error = self.check_file(file_path)
        if self.error:
            wx.MessageBox(self.error.message, "Error", wx.OK | wx.ICON_ERROR)
            self.parent.create_instance()
        else:
            super(MemcardViewFrame, self).__init__(*args, **kw, size=(960, 680))
            panel = wx.Panel(self)
            self.create_layout(panel)
            self.bind_events()
            self.on_load()

    def create_layout(self, panel: wx.Panel):
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.save_entries_list_box = wx.ListBox(panel, size=(200, 600))
        self.checkbox = wx.CheckBox(panel, label="汉化版")
        self.checkbox.SetValue(CnVersion.CN_VER)
        left_sizer.Add(self.save_entries_list_box)
        left_sizer.Add(self.checkbox, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.save_view_panel = SaveViewPanel(panel, self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(left_sizer)
        sizer.Add(self.save_view_panel)
        panel.SetSizer(sizer)

    def bind_events(self):
        self.Bind(wx.EVT_CLOSE, self.on_exit)
        self.Bind(wx.EVT_LISTBOX, self.on_select, self.save_entries_list_box)
        self.checkbox.Bind(wx.EVT_CHECKBOX, self.on_checkbox_click)

    def on_checkbox_click(self, evt: wx.Event):
        CnVersion.CN_VER = self.checkbox.IsChecked()
        self.save_view_panel.update_panels()

    def on_exit(self, evt: wx.Event):
        self.parent.create_instance()
        evt.Skip()

    def check_file(self, file_path: Path) -> Error:
        try:
            self.reader = MemcardReader(file_path)
            self.reader.load()
            self.save_entries = self.reader.read_save_entries()
            return None
        except Error as e:
            return e
        finally:
            self.reader.close()

    def on_load(self):
        for entry in self.save_entries:
            self.save_entries_list_box.Append(entry.name, entry)
        if self.save_entries:
            self.save_entries_list_box.SetSelection(0)
            self.save_view_panel._load_task(self.save_entries[0]) # TODO

    def on_select(self, evt: wx.Event):
        save_entry = self.save_entries_list_box.GetClientData(self.save_entries_list_box.GetSelection())
        self.save_view_panel.load(save_entry)

    def write_file(self, main_bytes: bytes, head_bytes: bytes = None):
        save_entry = self.save_entries_list_box.GetClientData(self.save_entries_list_box.GetSelection())
        self.reader.write_save_entry(save_entry, main_bytes, head_bytes)


class SaveViewPanel(wx.Panel):
    def __init__(self, parent: wx.Panel, root: wx.Frame):
        super().__init__(parent, size=(760, 680))
        self.root = root
        self.create_layout(self)
        self.bind_events()
        self.reader = None
        self.head_reader = None
        self.in_bit_stream = None
        self.out_bit_stream = None
        self.club = None
        self.my_team = None
        self.other_teams = None
        self.head = None

    def create_layout(self, panel: wx.Panel):
        self.notebook = wx.Notebook(panel)
        self.club_info_tab = ClubInfoTab(self.notebook, self)
        self.player_tab = PlayerTab(self.notebook, self)
        self.other_team_tab = OtherTeamTab(self.notebook, self)
        self.scout_tab = ScoutTab(self.notebook, self)
        self.notebook.AddPage(self.club_info_tab, "俱乐部")
        self.notebook.AddPage(self.player_tab, "我的球队")
        self.notebook.AddPage(self.other_team_tab, "其它球队")
        self.notebook.AddPage(self.scout_tab, "球探")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(sizer)
        panel.Centre()

    def bind_events(self):
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_changed)

    def load(self, save_entry: Saka04SaveEntry):
        threading.Thread(target=self._load_task, args=[save_entry]).start()

    def on_tab_changed(self, evt: wx.Event):
        page_index = evt.GetSelection()
        page = self.notebook.GetPage(page_index)
        page.load(self)
        evt.Skip()

    def _load_task(self, save_entry: Saka04SaveEntry):
        self.reader = SaveReader(save_entry.main_save_entry)
        self.reader.check_crc()
        self.reader.dec()
        decoded_byte_array = self.reader.decoded_data()
        self.in_bit_stream = InputBitStream(decoded_byte_array)
        self.out_bit_stream = OutputBitStream(decoded_byte_array)
        club_reader = ClubReader(self.in_bit_stream)
        self.club = club_reader.read()
        team_reader = TeamReader(self.in_bit_stream)
        self.my_team = team_reader.read()
        oteam_reader = OtherTeamReader(self.in_bit_stream)
        self.other_teams = oteam_reader.read()
        self.head_reader = SaveHeadReader(save_entry.save_head_entry)
        self.head_reader.check_crc()
        self.head = self.head_reader.read()

        wx.CallAfter(self._update_ui)

    def _update_ui(self):
        self.reset_panels()
        self.notebook.SetSelection(0)
        self.club_info_tab.load(self)
        self.update_panels()

    def save(self, bit_fields: list[IntBitField | StrBitField], byte_fields: list[IntByteField | StrByteField] = None):
        for bit_field in bit_fields:
            self.out_bit_stream.pack_bits(bit_field)
        self.reader.update_decode_buffer(self.out_bit_stream.input_data)
        encode_buffer = self.reader.enc()
        save_bin = self.reader.build_save_bytes(encode_buffer)
        head_bytes = None
        if byte_fields and len(byte_fields) > 0:
            for byte_field in byte_fields:
                self.head_reader.write(byte_field)
                head_bytes = self.head_reader.build_save_bytes()
        self.root.write_file(save_bin, head_bytes)
        wx.MessageBox('保存成功', APP_DISPLAY_NAME, style=wx.OK | wx.ICON_INFORMATION)

    def update_panels(self):
        self.club_info_tab.update()
        self.player_tab.update()
        self.other_team_tab.update()
        self.scout_tab.update()

    def reset_panels(self):
        self.club_info_tab.reset()
        self.player_tab.reset()
        self.other_team_tab.reset()
        self.scout_tab.reset()


class ClubInfoTab(wx.Panel):
    def __init__(self, parent: wx.Panel, root: wx.Panel):
        super().__init__(parent, size=(760, 680))
        self.root = root
        self.create_layout(self)
        self.bind_events()
        self.club = None
        self.head = None

    def create_layout(self, panel: wx.Panel):
        # Club Information group
        club_info_box = wx.StaticBox(panel, label="Club Information")
        club_info_sizer = wx.StaticBoxSizer(club_info_box, wx.VERTICAL)
        form_sizer = wx.FlexGridSizer(rows=5, cols=2, vgap=10, hgap=10)

        form_sizer.Add(wx.StaticText(panel, label="俱乐部:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.club_input = wx.TextCtrl(panel, size=(50, -1))
        self.club_input.SetEditable(False)
        form_sizer.Add(self.club_input, flag=wx.EXPAND)

        form_sizer.Add(wx.StaticText(panel, label="资金:"), flag=wx.ALIGN_CENTER_VERTICAL)
        fund_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.fund_input_billion = wx.SpinCtrl(panel, min=0, max=9999)  # 亿 input
        billion_label = wx.StaticText(panel, label="亿")
        self.fund_input_ten_thousand = wx.SpinCtrl(panel, min=0, max=9999)  # 万 input
        ten_thousand_label = wx.StaticText(panel, label="万")
        fund_sizer.Add(self.fund_input_billion, flag=wx.RIGHT, border=5)
        fund_sizer.Add(billion_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        fund_sizer.Add(self.fund_input_ten_thousand, flag=wx.RIGHT, border=5)
        fund_sizer.Add(ten_thousand_label, flag=wx.ALIGN_CENTER_VERTICAL)
        form_sizer.Add(fund_sizer, flag=wx.EXPAND)

        form_sizer.Add(wx.StaticText(panel, label="年份："), flag=wx.ALIGN_CENTER_VERTICAL)
        year_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.year_input = wx.SpinCtrl(panel, min=1, max=999)
        year_label = wx.StaticText(panel, label="年")
        self.month_input = wx.TextCtrl(panel, size=(50, -1))
        self.month_input.SetEditable(False)
        month_label = wx.StaticText(panel, label="月")
        self.date_input = wx.TextCtrl(panel, size=(50, -1))
        self.date_input.SetEditable(False)
        date_label = wx.StaticText(panel, label="日")
        year_sizer.Add(self.year_input, flag=wx.RIGHT, border=5)
        year_sizer.Add(year_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        year_sizer.Add(self.month_input, flag=wx.RIGHT, border=5)
        year_sizer.Add(month_label, flag=wx.ALIGN_CENTER_VERTICAL)
        year_sizer.Add(self.date_input, flag=wx.RIGHT, border=5)
        year_sizer.Add(date_label, flag=wx.ALIGN_CENTER_VERTICAL)
        form_sizer.Add(year_sizer, flag=wx.EXPAND)

        form_sizer.Add(wx.StaticText(panel, label="经理:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.manager_input = wx.TextCtrl(panel, size=(50, -1))
        self.manager_input.SetEditable(False)
        form_sizer.Add(self.manager_input, flag=wx.EXPAND)

        form_sizer.Add(wx.StaticText(panel, label="游戏难度:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.difficulty = wx.SpinCtrl(panel, min=0, max=31)
        form_sizer.Add(self.difficulty, flag=wx.EXPAND)

        club_info_sizer.Add(form_sizer, flag=wx.ALL | wx.EXPAND, border=10)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(club_info_sizer, flag=wx.ALL, border=10)
        self.submit_btn = wx.Button(panel, label="保存")
        sizer.Add(self.submit_btn, flag=wx.ALL, border=10)
        panel.SetSizer(sizer)


    def bind_events(self):
        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit_click)

    def on_submit_click(self, evt: wx.Event):
        self.club.set_funds(self.fund_input_billion.GetValue(), self.fund_input_ten_thousand.GetValue())
        self.club.year.value = self.year_input.GetValue() + 2003
        self.club.difficulty.value = self.difficulty.GetValue()
        bits_fields = list()
        bits_fields.append(self.club.funds)
        bits_fields.append(self.club.year)
        bits_fields.append(self.club.difficulty)
        self.head.year.value = self.year_input.GetValue() + 2003
        self.root.save(bits_fields, [self.head.year])

    def load(self, save_panel: SaveViewPanel):
        if self.club is None:
            self.club = save_panel.club
            self.head = save_panel.head
            self.update()

    def update(self):
        self.fund_input_billion.SetValue(self.club.funds_high)
        self.fund_input_ten_thousand.SetValue(self.club.funds_low)
        self.year_input.SetValue(self.club.year.value - 2003)
        self.month_input.SetLabelText(str(self.club.month.value))
        self.date_input.SetLabelText(str(self.club.date.value))
        self.manager_input.SetLabelText(self.club.manager_name.value)
        self.club_input.SetLabelText(self.club.club_name.value)
        self.difficulty.SetValue(self.club.difficulty.value)

    def reset(self):
        self.club = None
        self.head = None


class PlayerTab(wx.Panel):
    def __init__(self, parent, root: wx.Panel):
        super().__init__(parent)
        self.root = root
        self.create_layout(self)
        self.bind_events()
        self.team: MyTeam = None
        self.player: MyPlayer = None

    def create_layout(self, panel: wx.Panel):
        # player list box
        self.list_box = wx.ListBox(panel, size=(150, 480))
        self.edit_btn = wx.Button(panel, label="编辑")
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.list_box)
        left_sizer.Add(self.edit_btn, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        # Player Information group
        info_box = wx.StaticBox(panel, label="球员信息")
        info_sizer = wx.StaticBoxSizer(info_box, wx.VERTICAL)
        form_sizer = wx.FlexGridSizer(rows=14, cols=2, vgap=5, hgap=5)
        form_sizer.Add(wx.StaticText(panel, label="姓名:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_name_text = wx.TextCtrl(panel)
        self.player_name_text.SetEditable(False)
        form_sizer.Add(self.player_name_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="年龄:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_age_text = wx.TextCtrl(panel)
        self.player_age_text.SetEditable(False)
        form_sizer.Add(self.player_age_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="号码:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_number_text = wx.TextCtrl(panel)
        self.player_number_text.SetEditable(False)
        form_sizer.Add(self.player_number_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="出生地:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_born_text = wx.TextCtrl(panel)
        self.player_born_text.SetEditable(False)
        form_sizer.Add(self.player_born_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="惯用脚:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_foot_text = wx.TextCtrl(panel)
        self.player_foot_text.SetEditable(False)
        form_sizer.Add(self.player_foot_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="留学次数:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_aboard_times_text = wx.TextCtrl(panel)
        self.player_aboard_times_text.SetEditable(False)
        form_sizer.Add(self.player_aboard_times_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="位置:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_pos_text = wx.TextCtrl(panel)
        self.player_pos_text.SetEditable(False)
        form_sizer.Add(self.player_pos_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="风格:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_style_text = wx.TextCtrl(panel)
        self.player_style_text.SetEditable(False)
        form_sizer.Add(self.player_style_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="等级:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_rank_text = wx.TextCtrl(panel)
        self.player_rank_text.SetEditable(False)
        form_sizer.Add(self.player_rank_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="连携:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_teamwork_text = wx.TextCtrl(panel)
        self.player_teamwork_text.SetEditable(False)
        form_sizer.Add(self.player_teamwork_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="口调:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_tone_type_text = wx.TextCtrl(panel)
        self.player_tone_type_text.SetEditable(False)
        form_sizer.Add(self.player_tone_type_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="身体:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_grow_type_phy_text = wx.TextCtrl(panel)
        self.player_grow_type_phy_text.SetEditable(False)
        form_sizer.Add(self.player_grow_type_phy_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="技术:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_grow_type_tech_text = wx.TextCtrl(panel)
        self.player_grow_type_tech_text.SetEditable(False)
        form_sizer.Add(self.player_grow_type_tech_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="头脑:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_grow_type_sys_text = wx.TextCtrl(panel)
        self.player_grow_type_sys_text.SetEditable(False)
        form_sizer.Add(self.player_grow_type_sys_text, flag=wx.EXPAND)

        # form_sizer.Add(wx.StaticText(panel, label="magic:"), flag=wx.ALIGN_CENTER_VERTICAL)
        # self.player_magic_text = wx.TextCtrl(panel)
        # self.player_magic_text.SetEditable(False)
        # form_sizer.Add(self.player_magic_text, flag=wx.EXPAND)

        info_sizer.Add(form_sizer, flag=wx.ALL | wx.EXPAND, border=5)
        # player ability panel
        self.ability_panel = PlayerAbilPanel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(left_sizer, 0, wx.ALL, border=5)
        sizer.Add(info_sizer, 0, wx.ALL, border=5)
        sizer.Add(self.ability_panel, 0, wx.ALL, border=5)
        panel.SetSizerAndFit(sizer)

    def bind_events(self):
        self.Bind(wx.EVT_LISTBOX, self.on_select, self.list_box)
        self.edit_btn.Bind(wx.EVT_BUTTON, self.on_open_dialog)

    def load(self, save_panel: SaveViewPanel):
        if self.team is None:
            self.team = save_panel.my_team
            self.update()

    def update(self):
        if self.team:
            self.list_box.Clear()
            for player in self.team.sorted_players:
                if player.id.value != 0xFFFF:
                    self.list_box.Append(player.name.value, player)
            self.list_box.SetSelection(0)
            player = self.list_box.GetClientData(self.list_box.GetSelection())
            self.show_player(player)

    def reset(self):
        self.team = None
        self.player = None

    def on_select(self, evt: wx.Event):
        player = self.list_box.GetClientData(self.list_box.GetSelection())
        self.show_player(player)

    def show_player(self, player: MyPlayer):
        self.player = player
        self.player_name_text.SetLabelText(player.name.value)
        self.player_age_text.SetLabelText(str(player.age.value))
        self.player_born_text.SetLabelText(player.readable_born)
        self.player_foot_text.SetLabelText(player.prefer_foot)
        self.player_number_text.SetLabelText(str(player.number.value))
        self.player_aboard_times_text.SetLabelText(str(player.abroad_times.value))
        self.player_pos_text.SetLabelText(player.readable_pos)
        self.player_style_text.SetLabelText(player.readable_style)
        self.player_rank_text.SetLabelText(player.readable_rank)
        self.player_teamwork_text.SetLabelText(player.readable_cooperation_type)
        self.player_tone_type_text.SetLabelText(player.readable_tone_type)
        self.player_grow_type_phy_text.SetLabelText(player.get_readable_grow_type(player.grow_type_phy.value))
        self.player_grow_type_tech_text.SetLabelText(player.get_readable_grow_type(player.grow_type_tec.value))
        self.player_grow_type_sys_text.SetLabelText(player.get_readable_grow_type(player.grow_type_bra.value))
        # self.player_magic_text.SetLabelText(bin(player.magic_value.value))
        # print(player.un)
        self.ability_panel.update(player.abilities)

    def on_open_dialog(self, evt: wx.Event):
        dialog = PlayerEditDialog(self, self, self.player)
        dialog.ShowModal()
        dialog.Destroy()

    def on_save(self, bits_fields: list[IntBitField | StrBitField]):
        self.root.save(bits_fields)


class OtherTeamTab(wx.Panel):
    def __init__(self, parent, root: wx.Panel):
        super().__init__(parent)
        self.root = root
        self.create_layout(self)
        self.bind_events()
        self.teams = None
        self.selected_team = None
        self.group_index = {
            "日本": 0,
            "亚太": 30,
            "东欧": 54,
            "英国": 69,
            "法国": 93,
            "西班牙": 114,
            "葡萄牙": 134,
            "比利时": 152,
            "荷兰": 154,
            "意大利": 172,
            "德国": 190,
            "欧洲": 208,
            "非洲": 213,
            "巴西": 221,
            "阿根廷": 245,
            "美洲": 248,
        }

    def create_layout(self, panel: wx.Panel):
        self.tree = wx.TreeCtrl(self, style=wx.TR_DEFAULT_STYLE, size=(200, 600))
        self.tree.SetIndent(5)
        # Team Information group
        info_box = wx.StaticBox(panel, label="球队信息")
        info_sizer = wx.StaticBoxSizer(info_box, wx.VERTICAL)
        form_sizer = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=5)
        form_sizer.Add(wx.StaticText(panel, label="队名:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.team_name_text = wx.TextCtrl(panel, size=(150, 20))
        self.team_name_text.SetEditable(False)
        form_sizer.Add(self.team_name_text, flag=wx.ALL)
        form_sizer.Add(wx.StaticText(panel, label="友好度:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.team_friendly_text = wx.SpinCtrl(panel, size=(60, 20), min=0, max=255)
        form_sizer.Add(self.team_friendly_text, flag=wx.ALL)
        self.submit_btn = wx.Button(panel, label="保存", size=(40, 20))
        form_sizer.Add(self.submit_btn, flag=wx.ALL)
        info_sizer.Add(form_sizer, flag=wx.ALL | wx.EXPAND, border=0)

        self.grid = wx.grid.Grid(panel, size=(520, -1))
        self.grid.CreateGrid(25, 10)
        self.grid.SetColLabelValue(0, "姓名")
        self.grid.SetColSize(0, 75)
        self.grid.SetColLabelValue(1, "年龄")
        self.grid.SetColSize(1, 40)
        self.grid.SetColLabelValue(2, "号码")
        self.grid.SetColSize(2, 40)
        self.grid.SetColLabelValue(3, "位置")
        self.grid.SetColSize(3, 50)
        self.grid.SetColLabelValue(4, "等级")
        self.grid.SetColSize(4, 40)
        self.grid.SetColLabelValue(5, "连携")
        self.grid.SetColSize(5, 50)
        self.grid.SetColLabelValue(6, "口调")
        self.grid.SetColSize(6, 50)
        self.grid.SetColLabelValue(7, "身体")
        self.grid.SetColSize(7, 50)
        self.grid.SetColLabelValue(8, "技术")
        self.grid.SetColSize(8, 50)
        self.grid.SetColLabelValue(9, "头脑")
        self.grid.SetColSize(9, 50)
        self.grid.HideRowLabels()
        self.grid.SetColLabelSize(20)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(info_sizer, proportion=0, flag=wx.ALL, border=0)
        right_sizer.Add(self.grid, 0, flag=wx.EXPAND | wx.ALL, border=0)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.tree, 0, wx.ALL, border=5)
        sizer.Add(right_sizer, 0, wx.ALL, border=5)
        panel.SetSizer(sizer)

    def bind_events(self):
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_select)
        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit_click)

    def load(self, save_panel: SaveViewPanel):
        if self.teams is None:
            self.teams = save_panel.other_teams
            self.update()

    def update(self):
        if self.teams:
            self.tree.DeleteAllItems()
            root = self.tree.AddRoot("Teams")
            group_names = sorted(self.group_index.keys(), key=lambda k: self.group_index[k])
            for i, group_name in enumerate(group_names):
                start_index = self.group_index[group_name]
                end_index = self.group_index[group_names[i + 1]] if i + 1 < len(group_names) else len(self.teams)
                group_node = self.tree.AppendItem(root, group_name)
                for team in self.teams[start_index:end_index]:
                    team_item = self.tree.AppendItem(group_node, team.name)
                    self.tree.SetItemData(team_item, team)
            self.tree.Expand(root)

            if self.tree.ItemHasChildren(root):
                first_group, _ = self.tree.GetFirstChild(root)
                first_team, _ = self.tree.GetFirstChild(first_group)
                if first_team:
                    self.tree.SelectItem(first_team)
                    team = self.tree.GetItemData(first_team)
                    self.show_team(team)

    def reset(self):
        self.teams = None

    def on_select(self, evt: wx.Event):
        item = evt.GetItem()
        if item.IsOk():
            team = self.tree.GetItemData(item)
            if team:
                self.show_team(team)

    def on_submit_click(self, evt: wx.Event):
        self.selected_team.friendly.value = self.team_friendly_text.GetValue()
        self.root.save([self.selected_team.friendly])

    def show_team(self, team: OtherTeam):
        self.team_name_text.SetLabelText(team.name)
        self.team_friendly_text.SetValue(team.friendly.value)
        self.grid.ClearGrid()
        for i, player in enumerate([player for player in team.sorted_players if player.id.value != 0xffff]):
            self.grid.SetCellValue(i, 0, player.player.name)
            self.grid.SetCellValue(i, 1, str(player.age.value))
            self.grid.SetCellValue(i, 2, str(player.number.value))
            self.grid.SetCellValue(i, 3, player.player.pos)
            self.grid.SetCellValue(i, 4, player.player.rank)
            self.grid.SetCellValue(i, 5, player.player.team_work)
            self.grid.SetCellValue(i, 6, player.player.tone_type)
            self.grid.SetCellValue(i, 7, player.player.grow_type_phy)
            self.grid.SetCellValue(i, 8, player.player.grow_type_tech)
            self.grid.SetCellValue(i, 9, player.player.grow_type_sys)
        self.selected_team = team


class PlayerAbilPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, size=(400, 680))
        self.create_layout(self)

    def create_layout(self, panel: wx.Panel):
        scrolled_window = wx.ScrolledWindow(panel, style=wx.VSCROLL | wx.HSCROLL)
        scrolled_window.SetScrollRate(10, 10)
        form_sizer = wx.FlexGridSizer(rows=64, cols=3, vgap=10, hgap=10)
        self.gauge_list: list[PG.PyGauge] = list()
        self.text_list: list[wx.StaticText] = list()
        for i, ability_name in enumerate(PlayerAbility.ablility_list()):
            form_sizer.Add(wx.StaticText(scrolled_window, label=ability_name), flag=wx.ALIGN_CENTER_VERTICAL)
            gauge = PG.PyGauge(scrolled_window, -1, size=(100, 15), style=wx.GA_HORIZONTAL)
            gauge.SetValue([0, 0, 0])
            gauge.SetBarColor([wx.Colour(162, 255, 178), wx.Colour(255, 224, 130), wx.Colour(159, 176, 255)])
            gauge.SetBackgroundColour(wx.WHITE)
            gauge.SetBorderColor(wx.BLACK)
            gauge.SetBorderPadding(2)
            self.gauge_list.append(gauge)
            form_sizer.Add(gauge, flag=wx.ALIGN_CENTER_VERTICAL)
            ability_text = wx.StaticText(scrolled_window, label="")
            form_sizer.Add(ability_text, flag=wx.ALIGN_CENTER_VERTICAL)
            self.text_list.append(ability_text)
        scrolled_window.SetSizer(form_sizer)
        form_sizer.FitInside(scrolled_window)
        form_sizer.SetFlexibleDirection(wx.BOTH)
        form_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_NONE)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(scrolled_window, proportion=1, flag=wx.EXPAND)
        panel.SetSizer(main_sizer)

    def update(self, abilities: list[PlayerAbility]):
        for i, abilitiy in enumerate(abilities):
            self.gauge_list[i].SetValue([0, 0, 0])
            self.gauge_list[i].Update([self.calc_perce(abilitiy.current.value), self.calc_perce(abilitiy.current_max.value), self.calc_perce(abilitiy.max.value)], 100)
            self.text_list[i].SetLabelText(f"{abilitiy.current.value} | {abilitiy.current_max.value} | {abilitiy.max.value}")

    def calc_perce(self, n: int) -> int:
        r = int(n / 65535 * 100)
        return r or 1


class PlayerEditDialog(wx.Dialog):
    def __init__(self, parent, root: wx.Panel, player: MyPlayer):
        super().__init__(parent, title="球员编辑", size=(400, 520))
        self.root = root
        self.player = player
        self.player_ablities = list()
        self.ability_index = 0
        panel = wx.Panel(self)
        self.create_layout(panel)
        self.bind_events()
        self.load()

    def create_layout(self, panel: wx.Panel):
        sizer = wx.BoxSizer(wx.VERTICAL)
        form_sizer = wx.FlexGridSizer(rows=12, cols=2, vgap=10, hgap=10)
        form_sizer.Add(wx.StaticText(panel, label="姓名:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_name_text = wx.TextCtrl(panel)
        self.player_name_text.SetEditable(False)
        form_sizer.Add(self.player_name_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="年龄:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_age_text = wx.SpinCtrl(panel, min=16, max=40)
        form_sizer.Add(self.player_age_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="出生地:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.born_choice = wx.Choice(panel, choices=list(Region.region_dict().values()))
        form_sizer.Add(self.born_choice, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="位置:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.pos_choice = wx.Choice(panel, choices=list(Position.position_dict().values()))
        form_sizer.Add(self.pos_choice, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="风格:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.style_choice = wx.Choice(panel, choices=list(Style.style_dict().values()))
        form_sizer.Add(self.style_choice, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="连携:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.cooperation_choice = wx.Choice(panel, choices=list(CooperationType.cooperation_type_dict().values()))
        form_sizer.Add(self.cooperation_choice, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="口调:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.tone_choice = wx.Choice(panel, choices=list(ToneType.tone_type_dict().values()))
        form_sizer.Add(self.tone_choice, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="成长类型:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.grow_phy_choice = wx.Choice(panel, choices=list(GrowType.grow_type_dict().values()))
        self.grow_tec_choice = wx.Choice(panel, choices=list(GrowType.grow_type_dict().values()))
        self.grow_bra_choice = wx.Choice(panel, choices=list(GrowType.grow_type_dict().values()))
        grow_type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        grow_type_sizer.Add(self.grow_phy_choice)
        grow_type_sizer.Add(self.grow_tec_choice)
        grow_type_sizer.Add(self.grow_bra_choice)
        form_sizer.Add(grow_type_sizer, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="能力:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.ability_choice = wx.Choice(panel, choices=PlayerAbility.ablility_list())
        form_sizer.Add(self.ability_choice, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="能力值:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.ability_current_text = wx.SpinCtrl(panel, min=1, max=65535)
        self.ability_current_max_text = wx.SpinCtrl(panel, min=1, max=65535)
        self.ability_max_text = wx.SpinCtrl(panel, min=1, max=65535)
        ability_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ability_sizer.Add(self.ability_current_text)
        ability_sizer.Add(self.ability_current_max_text)
        ability_sizer.Add(self.ability_max_text)
        form_sizer.Add(ability_sizer, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label=""), flag=wx.ALIGN_CENTER_VERTICAL)
        self.current_max_btn = wx.Button(panel, label="所有能力到达当前上限")
        form_sizer.Add(self.current_max_btn, 0, flag=wx.ALIGN_RIGHT | wx.ALL)
        form_sizer.Add(wx.StaticText(panel, label=""), flag=wx.ALIGN_CENTER_VERTICAL)
        self.max_btn = wx.Button(panel, label="所有能力到达最高上限")
        form_sizer.Add(self.max_btn, 0, flag=wx.ALIGN_RIGHT | wx.ALL)

        sizer.Add(form_sizer, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        foot_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.close_btn = wx.Button(panel, label="Close")
        self.save_btn = wx.Button(panel, label="Save")
        foot_sizer.Add((0, 0), 1, wx.EXPAND)
        foot_sizer.Add(self.close_btn, wx.ALL, border=10)
        foot_sizer.Add(self.save_btn, wx.ALL, border=10)
        sizer.Add(foot_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)
        panel.SetSizer(sizer)

    def bind_events(self):
        self.close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_submit)
        self.current_max_btn.Bind(wx.EVT_BUTTON, self.on_current_max)
        self.max_btn.Bind(wx.EVT_BUTTON, self.on_max)
        self.ability_choice.Bind(wx.EVT_CHOICE, self.on_ability_select)
        self.ability_current_text.Bind(wx.EVT_SPINCTRL, self.on_current_changed)
        self.ability_current_max_text.Bind(wx.EVT_SPINCTRL, self.on_current_max_changed)
        self.ability_max_text.Bind(wx.EVT_SPINCTRL, self.on_max_changed)

    def load(self):
        self.player_name_text.SetValue(self.player.name.value)
        self.player_age_text.SetValue(self.player.age.value)
        self.ability_current_text.SetValue(self.player.abilities[0].current.value)
        self.ability_current_max_text.SetValue(self.player.abilities[0].current_max.value)
        self.ability_max_text.SetValue(self.player.abilities[0].max.value)
        for ability in self.player.abilities:
            self.player_ablities.append([ability.current.value, ability.current_max.value, ability.max.value])
        self.ability_choice.SetSelection(0)
        self.born_choice.SetStringSelection(self.player.readable_born)
        self.pos_choice.SetStringSelection(self.player.readable_pos)
        self.style_choice.SetStringSelection(self.player.readable_style)
        self.cooperation_choice.SetStringSelection(self.player.readable_cooperation_type)
        self.tone_choice.SetStringSelection(self.player.readable_tone_type)
        self.grow_phy_choice.SetStringSelection(self.player.get_readable_grow_type(self.player.grow_type_phy.value))
        self.grow_tec_choice.SetStringSelection(self.player.get_readable_grow_type(self.player.grow_type_tec.value))
        self.grow_bra_choice.SetStringSelection(self.player.get_readable_grow_type(self.player.grow_type_bra.value))

    def on_close(self, evt: wx.Event):
        self.EndModal(wx.ID_OK)

    def on_submit(self, evt: wx.Event):
        self.player.age.value = self.player_age_text.GetValue()
        selected_born = self.born_choice.GetStringSelection()
        self.player.born.value = Region.region_dict_reverse()[selected_born]
        self.player.born2.value = self.player.born.value
        selected_pos = self.pos_choice.GetStringSelection()
        self.player.pos.value = Position.position_dict_reverse()[selected_pos]
        self.player.pos2.value = self.player.pos.value
        selected_style = self.style_choice.GetStringSelection()
        self.player.style.value = Style.style_dict_reverse()[selected_style]
        self.player.style_equip.value = self.player.style.value
        self.player.set_style(self.style_choice.GetSelection())
        selected_cooperation_type = self.cooperation_choice.GetStringSelection()
        self.player.cooperation_type.value = CooperationType.cooperation_type_dict_reverse()[selected_cooperation_type]
        selected_tone_type = self.tone_choice.GetStringSelection()
        self.player.tone_type.value = ToneType.tone_type_dict_reverse()[selected_tone_type]
        selected_grow_type_phy = self.grow_phy_choice.GetStringSelection()
        selected_grow_type_tec = self.grow_tec_choice.GetStringSelection()
        selected_grow_type_bra = self.grow_bra_choice.GetStringSelection()
        self.player.grow_type_phy.value = GrowType.grow_type_dict_reverse()[selected_grow_type_phy]
        self.player.grow_type_tec.value = GrowType.grow_type_dict_reverse()[selected_grow_type_tec]
        self.player.grow_type_bra.value = GrowType.grow_type_dict_reverse()[selected_grow_type_bra]

        bits_fields = list()
        bits_fields.append(self.player.age)
        bits_fields.append(self.player.born)
        bits_fields.append(self.player.born2)
        bits_fields.append(self.player.pos)
        bits_fields.append(self.player.pos2)
        bits_fields.append(self.player.style)
        bits_fields.append(self.player.style_equip)
        bits_fields.append(self.player.style_learned1)
        bits_fields.append(self.player.style_learned2)
        bits_fields.append(self.player.cooperation_type)
        bits_fields.append(self.player.tone_type)
        bits_fields.append(self.player.grow_type_phy)
        bits_fields.append(self.player.grow_type_tec)
        bits_fields.append(self.player.grow_type_bra)

        for ability, ability_cache in zip(self.player.abilities, self.player_ablities):
            ability.current.value = ability_cache[0]
            ability.current_max.value = ability_cache[1]
            ability.max.value = ability_cache[2]

        for ability in self.player.abilities:
            bits_fields.append(ability.current)
            bits_fields.append(ability.current_max)
            bits_fields.append(ability.max)
        self.root.on_save(bits_fields)
        self.root.show_player(self.player)

    def on_ability_select(self, evt: wx.Event):
        selected_index = self.ability_choice.GetSelection()
        self.ability_current_text.SetValue(self.player.abilities[selected_index].current.value)
        self.ability_current_max_text.SetValue(self.player.abilities[selected_index].current_max.value)
        self.ability_max_text.SetValue(self.player.abilities[selected_index].max.value)
        self.ability_index = selected_index

    def on_current_changed(self, evt: wx.Event):
        value = evt.GetInt()
        self.player_ablities[self.ability_index][0] = value
        evt.Skip()

    def on_current_max_changed(self, evt: wx.Event):
        value = evt.GetInt()
        self.player_ablities[self.ability_index][1] = value
        evt.Skip()

    def on_max_changed(self, evt: wx.Event):
        value = evt.GetInt()
        self.player_ablities[self.ability_index][2] = value
        evt.Skip()

    def on_current_max(self, evt: wx.Event):
        for i, ability in enumerate(self.player.abilities):
            self.player_ablities[i][0] = ability.current_max.value
            self.player_ablities[i][1] = ability.current_max.value
        self.ability_current_text.SetValue(self.player_ablities[self.ability_index][0])
        self.ability_current_max_text.SetValue(self.player_ablities[self.ability_index][1])
        self.ability_max_text.SetValue(self.player_ablities[self.ability_index][2])

    def on_max(self, evt: wx.Event):
        for i, ability in enumerate(self.player.abilities):
            self.player_ablities[i][0] = ability.max.value
            self.player_ablities[i][1] = ability.max.value
        self.ability_current_text.SetValue(self.player_ablities[self.ability_index][0])
        self.ability_current_max_text.SetValue(self.player_ablities[self.ability_index][1])
        self.ability_max_text.SetValue(self.player_ablities[self.ability_index][2])


class ScoutTab(wx.Panel):
    def __init__(self, parent, root: wx.Panel):
        super().__init__(parent)
        self.root = root
        self.create_layout(self)
        self.bind_events()
        self.team: MyTeam = None
        # self.my_scout: MyScout = None
        # self.scout_candidate: Scout = None

    def create_layout(self, panel: wx.Panel):
        self.list_box = wx.ListBox(self, size=(150, 480))
        self.edit_btn = wx.Button(panel, label="编辑")
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.list_box)
        left_sizer.Add(self.edit_btn, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        info_box = wx.StaticBox(panel, label="球探信息")
        info_sizer = wx.StaticBoxSizer(info_box, wx.VERTICAL)
        form_sizer = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)

        form_sizer.Add(wx.StaticText(panel, label="姓名:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.name_text = wx.TextCtrl(panel)
        self.name_text.SetEditable(False)
        form_sizer.Add(self.name_text, flag=wx.EXPAND)

        form_sizer.Add(wx.StaticText(panel, label="年龄:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.age_text = wx.TextCtrl(panel)
        self.age_text.SetEditable(False)
        form_sizer.Add(self.age_text, flag=wx.EXPAND)

        form_sizer.Add(wx.StaticText(panel, label="得意地区1:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.area1_text = wx.TextCtrl(panel)
        self.area1_text.SetEditable(False)
        form_sizer.Add(self.area1_text, flag=wx.EXPAND)

        form_sizer.Add(wx.StaticText(panel, label="得意地区2:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.area2_text = wx.TextCtrl(panel)
        self.area2_text.SetEditable(False)
        form_sizer.Add(self.area2_text, flag=wx.EXPAND)

        info_sizer.Add(form_sizer, flag=wx.ALL | wx.EXPAND, border=5)

        self.ability_panel = ScoutAbilPanel(self)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(left_sizer, 0, wx.ALL, border=5)
        sizer.Add(info_sizer, 0, wx.ALL, border=5)
        sizer.Add(self.ability_panel, 0, wx.ALL, border=5)
        panel.SetSizer(sizer)

    def bind_events(self):
        self.list_box.Bind(wx.EVT_LISTBOX, self.on_select)
        # self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit_click)

    def load(self, save_panel: SaveViewPanel):
        if self.team is None:
            self.team = save_panel.my_team
            self.update()

    def on_select(self, evt: wx.Event):
        scout = self.list_box.GetClientData(self.list_box.GetSelection())
        self.show_scout(scout)

    def update(self):
        if self.team:
            self.list_box.Clear()
            for s in self.team.my_scouts:
                self.list_box.Append(s.saved_name.value, s)
            self.list_box.SetSelection(0)
            self.show_scout(self.team.my_scouts[0])

    def reset(self):
        self.team = None
        self.my_scout = None
        self.scout_candidate = None

    def show_scout(self, scout: Scout):
        self.name_text.SetLabelText(scout.saved_name.value)
        self.age_text.SetLabelText(str(scout.age.value))
        self.area1_text.SetLabelText(Region.get_region(scout.area1.value))
        self.area2_text.SetLabelText(Region.get_region(scout.area2.value))
        self.ability_panel.update(scout.abilities)

    def on_submit_click(self, evt: wx.Event):
        scout = self.list_box.GetClientData(self.list_box.GetSelection())
        bits_fields = list()
        for a in scout.abilities:
            a.value = 0x63
            bits_fields.append(a)
        self.root.save(bits_fields)


class ScoutAbilPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, size=(400, 680))
        self.create_layout(self)

    def create_layout(self, panel: wx.Panel):
        scrolled_window = wx.ScrolledWindow(panel, style=wx.VSCROLL | wx.HSCROLL)
        scrolled_window.SetScrollRate(10, 10)
        form_sizer = wx.FlexGridSizer(rows=21, cols=3, vgap=10, hgap=10)
        self.gauge_list: list[PG.PyGauge] = list()
        self.text_list: list[wx.StaticText] = list()
        for i, ability_name in enumerate(Scout.ablility_list()):
            form_sizer.Add(wx.StaticText(scrolled_window, label=ability_name), flag=wx.ALIGN_CENTER_VERTICAL)
            gauge = PG.PyGauge(scrolled_window, -1, size=(100, 15), style=wx.GA_HORIZONTAL)
            gauge.SetValue([0])
            gauge.SetBarColor([wx.Colour(162, 255, 178)])
            gauge.SetBackgroundColour(wx.WHITE)
            gauge.SetBorderColor(wx.BLACK)
            gauge.SetBorderPadding(2)
            self.gauge_list.append(gauge)
            form_sizer.Add(gauge, flag=wx.ALIGN_CENTER_VERTICAL)
            ability_text = wx.StaticText(scrolled_window, label="")
            form_sizer.Add(ability_text, flag=wx.ALIGN_CENTER_VERTICAL)
            self.text_list.append(ability_text)
        scrolled_window.SetSizer(form_sizer)
        form_sizer.FitInside(scrolled_window)
        form_sizer.SetFlexibleDirection(wx.BOTH)
        form_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_NONE)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(scrolled_window, proportion=1, flag=wx.EXPAND)
        panel.SetSizer(main_sizer)

    def update(self, abilities: list[IntBitField]):
        for i, abilitiy in enumerate(abilities):
            self.gauge_list[i].SetValue([0])
            self.gauge_list[i].Update([abilitiy.value], 100)
            self.text_list[i].SetLabelText(f"{abilitiy.value}")
