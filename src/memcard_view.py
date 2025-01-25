from pathlib import Path
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
            super(MemcardViewFrame, self).__init__(*args, **kw, size=(960, 640))
            panel = wx.Panel(self)
            self.create_layout(panel)
            self.bind_events()
            self.on_load()

    def create_layout(self, panel: wx.Panel):
        self.save_entries_list_box = wx.ListBox(panel, size=(200, 640))
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

    def bind_events(self):
        self.checkbox.Bind(wx.EVT_CHECKBOX, self.on_checkbox_click)
        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit_click)

    def load(self, byte_array: bytes):
        self.reader = SaveReader(byte_array)
        self.reader.check_crc()
        self.reader.dec()
        decoded_byte_array = self.reader.decoded_data()
        self.in_bit_stream = InputBitStream(decoded_byte_array)
        self.out_bit_stream = OutputBitStream(decoded_byte_array)
        club_reader = ClubReader(self.in_bit_stream)
        club = club_reader.read()
        self.club_info_tab.load(club)
        team_reader = TeamReader(self.in_bit_stream)
        my_team = team_reader.read()
        self.player_tab.load(my_team)
        oteam_reader = OtherTeamReader(self.in_bit_stream)
        other_teams = oteam_reader.read()
        self.other_team_tab.load(other_teams)
        self.update_panels()

    def on_checkbox_click(self, evt: wx.Event):
        CnVersion.CN_VER = self.checkbox.IsChecked()
        self.update_panels()

    def on_submit_click(self, evt: wx.Event):
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
        self.list_box = wx.ListBox(panel, size=(200, 480))
        # Player Information group
        info_box = wx.StaticBox(panel, label="球员信息")
        info_sizer = wx.StaticBoxSizer(info_box, wx.VERTICAL)
        form_sizer = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        form_sizer.Add(wx.StaticText(panel, label="姓名:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_name_text = wx.TextCtrl(panel)
        form_sizer.Add(self.player_name_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="年龄:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_age_text = wx.TextCtrl(panel)
        form_sizer.Add(self.player_age_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="出生:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.player_born_text = wx.TextCtrl(panel)
        form_sizer.Add(self.player_born_text, flag=wx.EXPAND)
        info_sizer.Add(form_sizer, flag=wx.ALL | wx.EXPAND, border=10)
        # player ability panel
        self.ability_panel = PlayerAbilPanel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.list_box)
        sizer.Add(info_sizer)
        sizer.Add(self.ability_panel)
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

    def on_select(self, evt: wx.Event):
        player = self.list_box.GetClientData(self.list_box.GetSelection())
        self.show_player(player)

    def show_player(self, player: MyPlayer):
        self.player_name_text.SetLabelText(player.name.value)
        self.player_age_text.SetLabelText(str(player.age.value))
        self.player_born_text.SetLabelText(str(player.born.value))
        self.ability_panel.update(player.abilities)


class OtherTeamTab(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_layout(self)
        self.bind_events()
        self.teams = None

    def create_layout(self, panel: wx.Panel):
        self.list_box = wx.ListBox(self, size=(250, 640))
        # Team Information group
        info_box = wx.StaticBox(panel, label="球队信息")
        info_sizer = wx.StaticBoxSizer(info_box, wx.VERTICAL)
        form_sizer = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        form_sizer.Add(wx.StaticText(panel, label="球队名称:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.team_name_text = wx.TextCtrl(panel)
        form_sizer.Add(self.team_name_text, flag=wx.EXPAND)
        form_sizer.Add(wx.StaticText(panel, label="友好度:"), flag=wx.ALIGN_CENTER_VERTICAL)
        self.team_friendly_text = wx.TextCtrl(panel)
        form_sizer.Add(self.team_friendly_text, flag=wx.EXPAND)
        info_sizer.Add(form_sizer, flag=wx.ALL | wx.EXPAND, border=10)
        self.grid = wx.grid.Grid(panel)
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
        panel.SetSizer(sizer)

    def bind_events(self):
        self.Bind(wx.EVT_LISTBOX, self.on_select, self.list_box)

    def load(self, teams: list[OtherTeam]):
        self.teams = teams

    def update(self):
        self.list_box.Clear()
        for team in self.teams:
            self.list_box.Append(team.name, team)

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


class PlayerAbilPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, size=(400, 640))
        self.create_layout(self)

    def create_layout(self, panel: wx.Panel):
        scrolled_window = wx.ScrolledWindow(panel, style=wx.VSCROLL | wx.HSCROLL)
        scrolled_window.SetScrollRate(10, 10)
        form_sizer = wx.FlexGridSizer(rows=64, cols=3, vgap=10, hgap=10)
        self.gauge_list: list[PG.PyGauge] = list()
        self.text_list: list[wx.StaticText] = list()
        for ability_name in PlayerAbility.ablility_list():
            form_sizer.Add(wx.StaticText(scrolled_window, label=ability_name), flag=wx.ALIGN_CENTER_VERTICAL)
            gauge = PG.PyGauge(scrolled_window, -1, size=(100, 20), style=wx.GA_HORIZONTAL)
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
        return int(n / 65535 * 100)