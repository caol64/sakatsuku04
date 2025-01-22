from pathlib import Path
import wx
import wx.grid

from bit_stream import InputBitStream
from memcard_reader import MemcardReader, Saka04SaveEntry
from models import MyPlayer, OtherTeam
from readers import ClubReader, OtherTeamReader, TeamReader
from save_reader import SaveReader
from utils import CnVersion


class MemcardViewFrame(wx.Frame):
    def __init__(self, *args, file_path: Path, parent: wx.Frame, **kw):
        super(MemcardViewFrame, self).__init__(*args, **kw, size=(960, 640))
        self.file_path = file_path
        self.parent = parent
        self.Bind(wx.EVT_CLOSE, self.on_exit)
        panel = wx.Panel(self)
        self.save_entries_list_box = wx.ListBox(panel, size=(200, 640))
        self.Bind(wx.EVT_LISTBOX, self.on_select, self.save_entries_list_box)
        self.save_view_panel = SaveViewPanel(panel)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.save_entries_list_box)
        sizer.Add(self.save_view_panel)
        panel.SetSizer(sizer)
        self.save_entries: list[Saka04SaveEntry] = list()
        self.on_load()

    def on_exit(self, evt: wx.Event):
        self.parent.create_instance()
        evt.Skip()

    def on_load(self):
        reader = MemcardReader(self.file_path)
        try:
            reader.load()
            self.save_entries = reader.read_save_entries()
            for entry in self.save_entries:
                self.save_entries_list_box.Append(entry.name, entry)
        finally:
            reader.close()

    def on_select(self, evt: wx.Event):
        save_entry = self.save_entries_list_box.GetClientData(self.save_entries_list_box.GetSelection())
        self.save_view_panel.load(save_entry.main_save_entry)


class SaveViewPanel(wx.Panel):
    def __init__(self, parent: wx.Panel):
        super().__init__(parent)
        notebook = wx.Notebook(self)
        self.club_info_tab = ClubInfoTab(notebook)
        self.player_tab = PlayerTab(notebook)
        self.other_team_tab = OtherTeamTab(notebook)
        notebook.AddPage(self.club_info_tab, "俱乐部")
        notebook.AddPage(self.player_tab, "我的球队")
        notebook.AddPage(self.other_team_tab, "其它球队")
        self.checkbox = wx.CheckBox(self, label="汉化版")
        self.checkbox.Bind(wx.EVT_CHECKBOX, self.on_checkbox_click)
        self.submit_btn = wx.Button(self, label="保存")
        footer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        footer_sizer.Add((0, 0), 1, wx.EXPAND)
        footer_sizer.Add(self.checkbox, 0, wx.ALL, 5)
        footer_sizer.Add(self.submit_btn, 0, wx.ALL, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(footer_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
        self.Centre()
        self.club, self.my_team, self.other_teams = None, None, None

    def load(self, byte_array: bytes):
        reader = SaveReader(byte_array)
        reader.check_crc()
        reader.dec()
        bit_stream = InputBitStream(reader.decoded_data())
        club_reader = ClubReader(bit_stream)
        self.club = club_reader.read()
        self.club_info_tab.fund_input_billion.SetValue(self.club.funds_high)
        self.club_info_tab.fund_input_ten_thousand.SetValue(self.club.funds_low)
        self.club_info_tab.year_input.SetLabelText(str(self.club.year.value - 2003))
        self.club_info_tab.month_input.SetLabelText(str(self.club.month.value))
        self.club_info_tab.date_input.SetLabelText(str(self.club.date.value))
        self.club_info_tab.manager_input.SetLabelText(self.club.manager_name.value)
        self.club_info_tab.club_input.SetLabelText(self.club.club_name.value)
        team_reader = TeamReader(bit_stream)
        self.my_team = team_reader.read()
        oteam_reader = OtherTeamReader(bit_stream)
        self.other_teams = oteam_reader.read()
        self.update_panel()

    def on_checkbox_click(self, evt: wx.Event):
        CnVersion.CN_VER = self.checkbox.IsChecked()
        self.update_panel()

    def update_panel(self):
        self.club_info_tab.manager_input.SetLabelText(self.club.manager_name.value)
        self.club_info_tab.club_input.SetLabelText(self.club.club_name.value)
        self.player_tab.list_box.Clear()
        for player in self.my_team.players:
            if player.id.value != 0xFFFF:
                self.player_tab.list_box.Append(player.name.value, player)
        self.other_team_tab.list_box.Clear()
        for team in self.other_teams:
            self.other_team_tab.list_box.Append(team.name, team)


class ClubInfoTab(wx.Panel):
    def __init__(self, parent: wx.Panel):
        super().__init__(parent)
        # Club Information group
        club_info_box = wx.StaticBox(self, label="Club Information")
        club_info_sizer = wx.StaticBoxSizer(club_info_box, wx.VERTICAL)
        form_sizer = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)

        form_sizer.Add(wx.StaticText(self, label="资金:"), flag=wx.ALIGN_CENTER_VERTICAL)
        fund_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.fund_input_billion = wx.SpinCtrl(self, min=0, max=9999)  # 亿 input
        billion_label = wx.StaticText(self, label="亿")
        self.fund_input_ten_thousand = wx.SpinCtrl(self, min=0, max=9999)  # 万 input
        ten_thousand_label = wx.StaticText(self, label="万")
        fund_sizer.Add(self.fund_input_billion, flag=wx.RIGHT, border=5)
        fund_sizer.Add(billion_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        fund_sizer.Add(self.fund_input_ten_thousand, flag=wx.RIGHT, border=5)
        fund_sizer.Add(ten_thousand_label, flag=wx.ALIGN_CENTER_VERTICAL)
        form_sizer.Add(fund_sizer, flag=wx.EXPAND)

        form_sizer.Add(wx.StaticText(self, label="年份："), flag=wx.ALIGN_CENTER_VERTICAL)
        year_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.year_input = wx.TextCtrl(self, size=(50, -1))
        year_label = wx.StaticText(self, label="年")
        self.month_input = wx.TextCtrl(self, size=(50, -1))
        month_label = wx.StaticText(self, label="月")
        self.date_input = wx.TextCtrl(self, size=(50, -1))
        date_label = wx.StaticText(self, label="日")
        year_sizer.Add(self.year_input, flag=wx.RIGHT, border=5)
        year_sizer.Add(year_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
        year_sizer.Add(self.month_input, flag=wx.RIGHT, border=5)
        year_sizer.Add(month_label, flag=wx.ALIGN_CENTER_VERTICAL)
        year_sizer.Add(self.date_input, flag=wx.RIGHT, border=5)
        year_sizer.Add(date_label, flag=wx.ALIGN_CENTER_VERTICAL)
        form_sizer.Add(year_sizer, flag=wx.EXPAND)

        form_sizer.Add(wx.StaticText(self, label="经理:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.manager_input = wx.TextCtrl(self, size=(50, -1))
        form_sizer.Add(self.manager_input, flag=wx.EXPAND)

        form_sizer.Add(wx.StaticText(self, label="俱乐部:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.club_input = wx.TextCtrl(self, size=(50, -1))
        form_sizer.Add(self.club_input, flag=wx.EXPAND)

        club_info_sizer.Add(form_sizer, flag=wx.ALL | wx.EXPAND, border=10)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(club_info_sizer, flag=wx.ALL, border=10)
        self.SetSizer(sizer)


class PlayerTab(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.list_box = wx.ListBox(self, size=(200, 480))
        self.Bind(wx.EVT_LISTBOX, self.on_select, self.list_box)
        # Player Information group
        info_box = wx.StaticBox(self, label="球员信息")
        info_sizer = wx.StaticBoxSizer(info_box, wx.VERTICAL)
        form_sizer = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        form_sizer.Add(wx.StaticText(self, label="姓名:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_name_text = wx.TextCtrl(self)
        form_sizer.Add(self.player_name_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(self, label="年龄:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_age_text = wx.TextCtrl(self)
        form_sizer.Add(self.player_age_text, flag=wx.EXPAND)
        info_sizer.Add(form_sizer, flag=wx.ALL | wx.EXPAND, border=10)
        self.grid = wx.grid.Grid(self)
        self.grid.CreateGrid(64, 4)
        self.grid.SetColLabelValue(0, "")
        self.grid.SetColLabelValue(1, "当前")
        self.grid.SetColLabelValue(2, "当前上限")
        self.grid.SetColLabelValue(3, "最高上限")
        for i in range(4):
            self.grid.SetColSize(i, 70)
        self.grid.SetSize(300, 640)
        self.grid.SetMinSize((300, 640))
        self.grid.HideRowLabels()
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.list_box)
        sizer.Add(info_sizer)
        sizer.Add(self.grid)
        self.SetSizerAndFit(sizer)

    def on_select(self, evt: wx.Event):
        player = self.list_box.GetClientData(self.list_box.GetSelection())
        self.show_player(player)

    def show_player(self, player: MyPlayer):
        self.player_name_text.SetLabelText(player.name.value)
        self.player_age_text.SetLabelText(str(player.age.value))
        for i, abilities in enumerate(player.abilities):
            self.grid.SetCellValue(i, 0, abilities.name)
            self.grid.SetCellValue(i, 1, str(abilities.current.value))
            self.grid.SetCellValue(i, 2, str(abilities.current_max.value))
            self.grid.SetCellValue(i, 3, str(abilities.max.value))

class OtherTeamTab(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.list_box = wx.ListBox(self, size=(250, 640))
        self.Bind(wx.EVT_LISTBOX, self.on_select, self.list_box)
        # Team Information group
        info_box = wx.StaticBox(self, label="球队信息")
        info_sizer = wx.StaticBoxSizer(info_box, wx.VERTICAL)
        form_sizer = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        form_sizer.Add(wx.StaticText(self, label="球队名称:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.team_name_text = wx.TextCtrl(self)
        form_sizer.Add(self.team_name_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(self, label="友好度:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.team_friendly_text = wx.TextCtrl(self)
        form_sizer.Add(self.team_friendly_text, flag=wx.EXPAND)
        info_sizer.Add(form_sizer, flag=wx.ALL | wx.EXPAND, border=10)
        self.grid = wx.grid.Grid(self)
        self.grid.CreateGrid(25, 4)
        self.grid.SetColLabelValue(0, "姓名")
        self.grid.SetColLabelValue(1, "年龄")
        self.grid.SetColLabelValue(2, "号码")
        self.grid.SetColLabelValue(3, "球探标识")
        for i in range(4):
            self.grid.SetColSize(i, 75)
        self.grid.HideRowLabels()
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.list_box)
        sizer.Add(info_sizer)
        sizer.Add(self.grid)
        self.SetSizer(sizer)

    def on_select(self, evt: wx.Event):
        team = self.list_box.GetClientData(self.list_box.GetSelection())
        self.show_team(team)

    def show_team(self, team: OtherTeam):
        self.team_name_text.SetLabelText(team.name)
        self.team_friendly_text.SetLabelText(str(team.friendly.value))
        self.grid.ClearGrid()
        for i, player in enumerate([player for player in team.players if player.id.value != 0xffff]):
            self.grid.SetCellValue(i, 0, player.name)
            self.grid.SetCellValue(i, 1, str(player.age.value))
            self.grid.SetCellValue(i, 2, str(player.number.value))
            self.grid.SetCellValue(i, 3, str(player.ability_graph.value))