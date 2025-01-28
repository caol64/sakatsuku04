from pathlib import Path
import threading
import wx
import wx.grid
import wx.lib.agw.pygauge as PG

from bit_stream import InputBitStream, OutputBitStream
from error import Error
from memcard_reader import MemcardReader
from models import Club, MyPlayer, MyTeam, OtherTeam, PlayerAbility
from readers import ClubReader, OtherTeamReader, TeamReader
from save_reader import SaveReader
from utils import CnVersion


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
        self.save_entries_list_box = wx.ListBox(panel, size=(200, 680))
        self.save_view_panel = SaveViewPanel(panel, self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.save_entries_list_box)
        sizer.Add(self.save_view_panel)
        panel.SetSizer(sizer)

    def bind_events(self):
        self.Bind(wx.EVT_CLOSE, self.on_exit)
        self.Bind(wx.EVT_LISTBOX, self.on_select, self.save_entries_list_box)

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
            self.save_view_panel.load(self.save_entries[0].main_save_entry)
            self.save_entries_list_box.SetSelection(0)

    def on_select(self, evt: wx.Event):
        save_entry = self.save_entries_list_box.GetClientData(self.save_entries_list_box.GetSelection())
        self.save_view_panel.load(save_entry.main_save_entry)

    def write_file(self, byte_array: bytes):
        save_entry = self.save_entries_list_box.GetClientData(self.save_entries_list_box.GetSelection())
        self.reader.write_save_entry(save_entry, byte_array)


class SaveViewPanel(wx.Panel):
    def __init__(self, parent: wx.Panel, root: wx.Frame):
        super().__init__(parent)
        self.root = root
        self.create_layout(self)
        self.bind_events()
        self.reader = None
        self.in_bit_stream = None
        self.out_bit_stream = None
        self.club = None
        self.my_team = None
        self.other_teams = None

    def create_layout(self, panel: wx.Panel):
        notebook = wx.Notebook(panel)
        self.club_info_tab = ClubInfoTab(notebook)
        self.player_tab = PlayerTab(notebook)
        self.other_team_tab = OtherTeamTab(notebook)
        notebook.AddPage(self.club_info_tab, "俱乐部")
        notebook.AddPage(self.player_tab, "我的球队")
        notebook.AddPage(self.other_team_tab, "其它球队")
        self.checkbox = wx.CheckBox(panel, label="汉化版")
        self.checkbox.SetValue(CnVersion.CN_VER)
        self.submit_btn = wx.Button(panel, label="保存")
        footer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        footer_sizer.Add((0, 0), 1, wx.EXPAND)
        footer_sizer.Add(self.checkbox, 0, wx.ALL, 5)
        footer_sizer.Add(self.submit_btn, 0, wx.ALL, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(footer_sizer, 0, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(sizer)
        panel.Centre()
        self.notebook = notebook

    def bind_events(self):
        self.checkbox.Bind(wx.EVT_CHECKBOX, self.on_checkbox_click)
        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit_click)

    def load(self, byte_array: bytes):
        threading.Thread(target=self._load_task, args=(byte_array,)).start()

    def _load_task(self, byte_array: bytes):
        self.reader = SaveReader(byte_array)
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
        wx.CallAfter(self._update_ui)

    def _update_ui(self):
        self.club_info_tab.load(self.club)
        self.player_tab.load(self.my_team)
        self.other_team_tab.load(self.other_teams)
        self.update_panels()
        self.notebook.SetSelection(0)

    def on_checkbox_click(self, evt: wx.Event):
        CnVersion.CN_VER = self.checkbox.IsChecked()
        self.update_panels()

    def on_submit_click(self, evt: wx.Event):
        # wx.MessageBox('', '敬请期待', style=wx.OK | wx.ICON_INFORMATION)
        self.club_info_tab.submit(self.out_bit_stream)
        self.reader.update_decode_buffer(self.out_bit_stream.input_data)
        encode_buffer = self.reader.enc()
        save_bin = self.reader.build_save_bytes(encode_buffer)
        self.root.write_file(save_bin)

    def update_panels(self):
        self.club_info_tab.update()
        self.player_tab.update()
        self.other_team_tab.update()


class ClubInfoTab(wx.Panel):
    def __init__(self, parent: wx.Panel):
        super().__init__(parent)
        self.create_layout(self)
        self.club = None

    def create_layout(self, panel: wx.Panel):
        # Club Information group
        club_info_box = wx.StaticBox(panel, label="Club Information")
        club_info_sizer = wx.StaticBoxSizer(club_info_box, wx.VERTICAL)
        form_sizer = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)

        form_sizer.Add(wx.StaticText(panel, label="俱乐部:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.club_input = wx.TextCtrl(panel, size=(50, -1))
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
        self.year_input = wx.TextCtrl(panel, size=(50, -1))
        year_label = wx.StaticText(panel, label="年")
        self.month_input = wx.TextCtrl(panel, size=(50, -1))
        month_label = wx.StaticText(panel, label="月")
        self.date_input = wx.TextCtrl(panel, size=(50, -1))
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
        form_sizer.Add(self.manager_input, flag=wx.EXPAND)

        club_info_sizer.Add(form_sizer, flag=wx.ALL | wx.EXPAND, border=10)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(club_info_sizer, flag=wx.ALL, border=10)
        panel.SetSizer(sizer)

    def load(self, club: Club):
        self.club = club

    def update(self):
        self.fund_input_billion.SetValue(self.club.funds_high)
        self.fund_input_ten_thousand.SetValue(self.club.funds_low)
        self.year_input.SetLabelText(str(self.club.year.value - 2003))
        self.month_input.SetLabelText(str(self.club.month.value))
        self.date_input.SetLabelText(str(self.club.date.value))
        self.manager_input.SetLabelText(self.club.manager_name.value)
        self.club_input.SetLabelText(self.club.club_name.value)

    def submit(self, bit_stream: OutputBitStream):
        self.club.set_funds(self.fund_input_billion.GetValue(), self.fund_input_ten_thousand.GetValue())
        bit_stream.pack_bits(self.club.funds)

class PlayerTab(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_layout(self)
        self.bind_events()
        self.team = None

    def create_layout(self, panel: wx.Panel):
        # player list box
        self.list_box = wx.ListBox(panel, size=(150, 480))
        # Player Information group
        info_box = wx.StaticBox(panel, label="球员信息")
        info_sizer = wx.StaticBoxSizer(info_box, wx.VERTICAL)
        form_sizer = wx.FlexGridSizer(rows=12, cols=2, vgap=5, hgap=5)
        form_sizer.Add(wx.StaticText(panel, label="姓名:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_name_text = wx.TextCtrl(panel)
        form_sizer.Add(self.player_name_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="年龄:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_age_text = wx.TextCtrl(panel)
        form_sizer.Add(self.player_age_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="号码:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_number_text = wx.TextCtrl(panel)
        form_sizer.Add(self.player_number_text, flag=wx.EXPAND)
        # form_sizer.Add(wx.StaticText(panel, label="出生:"), flag=wx.ALIGN_CENTER_VERTICAL)
        # self.player_born_text = wx.TextCtrl(panel)
        # form_sizer.Add(self.player_born_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="惯用脚:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_foot_text = wx.TextCtrl(panel)
        form_sizer.Add(self.player_foot_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="留学次数:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_aboard_times_text = wx.TextCtrl(panel)
        form_sizer.Add(self.player_aboard_times_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="位置:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_pos_text = wx.TextCtrl(panel)
        form_sizer.Add(self.player_pos_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="等级:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_rank_text = wx.TextCtrl(panel)
        form_sizer.Add(self.player_rank_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="连携:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_teamwork_text = wx.TextCtrl(panel)
        form_sizer.Add(self.player_teamwork_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="口调:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_tone_type_text = wx.TextCtrl(panel)
        form_sizer.Add(self.player_tone_type_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="身体:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_grow_type_phy_text = wx.TextCtrl(panel)
        form_sizer.Add(self.player_grow_type_phy_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="技术:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_grow_type_tech_text = wx.TextCtrl(panel)
        form_sizer.Add(self.player_grow_type_tech_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="头脑:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_grow_type_sys_text = wx.TextCtrl(panel)
        form_sizer.Add(self.player_grow_type_sys_text, flag=wx.EXPAND)
        info_sizer.Add(form_sizer, flag=wx.ALL | wx.EXPAND, border=5)
        # player ability panel
        self.ability_panel = PlayerAbilPanel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.list_box, 0, wx.ALL, border=5)
        sizer.Add(info_sizer, 0, wx.ALL, border=5)
        sizer.Add(self.ability_panel, 0, wx.ALL, border=5)
        panel.SetSizerAndFit(sizer)

    def bind_events(self):
        self.Bind(wx.EVT_LISTBOX, self.on_select, self.list_box)

    def load(self, team: MyTeam):
        self.team = team

    def update(self):
        self.list_box.Clear()
        for player in self.team.players:
            if player.id.value != 0xFFFF:
                self.list_box.Append(player.name.value, player)
        self.list_box.SetSelection(0)
        player = self.list_box.GetClientData(self.list_box.GetSelection())
        self.show_player(player)

    def on_select(self, evt: wx.Event):
        player = self.list_box.GetClientData(self.list_box.GetSelection())
        self.show_player(player)

    def show_player(self, player: MyPlayer):
        self.player_name_text.SetLabelText(player.name.value)
        self.player_age_text.SetLabelText(str(player.age.value))
        # self.player_born_text.SetLabelText(str(player.born.value))
        self.player_foot_text.SetLabelText(player.prefer_foot)
        self.player_number_text.SetLabelText(str(player.number.value))
        self.player_aboard_times_text.SetLabelText(str(player.abroad_times.value))
        self.player_pos_text.SetLabelText(player.player.pos)
        self.player_rank_text.SetLabelText(player.player.rank)
        self.player_teamwork_text.SetLabelText(player.player.team_work)
        self.player_tone_type_text.SetLabelText(player.player.tone_type)
        self.player_grow_type_phy_text.SetLabelText(player.player.grow_type_phy)
        self.player_grow_type_tech_text.SetLabelText(player.player.grow_type_tech)
        self.player_grow_type_sys_text.SetLabelText(player.player.grow_type_sys)
        self.ability_panel.update(player.abilities)


class OtherTeamTab(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_layout(self)
        self.bind_events()
        self.teams = None
        self.group_index = {
            "日本": 0,
            "亚太": 30,
            "东欧": 54,
            "英国": 69,
            "法国": 93,
            "西班牙": 115,
            "葡萄牙": 134,
            "比利时": 152,
            "荷兰": 154,
            "意大利": 172,
            "德国": 190,
            "欧洲": 208,
            "非洲": 214,
            "巴西": 221,
            "阿根廷": 245,
            "美洲": 248,
        }

    def create_layout(self, panel: wx.Panel):
        self.tree = wx.TreeCtrl(self, style=wx.TR_DEFAULT_STYLE, size=(200, 440))
        # Team Information group
        info_box = wx.StaticBox(panel, label="球队信息", size=(200, 200))
        info_sizer = wx.StaticBoxSizer(info_box, wx.VERTICAL)
        form_sizer = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        form_sizer.Add(wx.StaticText(panel, label="队名:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.team_name_text = wx.TextCtrl(panel)
        form_sizer.Add(self.team_name_text, flag=wx.ALL)
        form_sizer.Add(wx.StaticText(panel, label="友好度:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.team_friendly_text = wx.TextCtrl(panel)
        form_sizer.Add(self.team_friendly_text, flag=wx.ALL)
        info_sizer.Add(form_sizer, flag=wx.ALL | wx.EXPAND, border=5)

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.tree, 0, wx.ALL, border=5)
        left_sizer.Add(info_sizer, 0, wx.ALL, border=5)

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
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(left_sizer, 0, wx.ALL, border=5)
        sizer.Add(self.grid, 0, wx.ALL, border=5)
        panel.SetSizer(sizer)

    def bind_events(self):
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_select)

    def load(self, teams: list[OtherTeam]):
        self.teams = teams

    def update(self):
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

    def on_select(self, evt: wx.Event):
        item = evt.GetItem()
        if item.IsOk():
            team = self.tree.GetItemData(item)
            if team:
                self.show_team(team)

    def show_team(self, team: OtherTeam):
        self.team_name_text.SetLabelText(team.name)
        self.team_friendly_text.SetLabelText(str(team.friendly.value))
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
        for ability_name in PlayerAbility.ablility_list():
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
            self.text_list[i].SetLabelText(f"{abilitiy.current.value}/{abilitiy.current_max.value}/{abilitiy.max.value}")

    def calc_perce(self, n: int) -> int:
        r = int(n / 65535 * 100)
        return r or 1