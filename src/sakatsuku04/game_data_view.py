from pathlib import Path
import wx
import wx.grid

from .game_data_reader import DataPacReader, PlayerData


class DataViewFrame(wx.Frame):
    def __init__(self, *args, file_path: Path, parent: wx.Frame, **kw):
        super(DataViewFrame, self).__init__(*args, **kw, size=(640, 480))
        self.file_path = file_path
        self.parent = parent
        self.error = None
        panel = wx.Panel(self)
        self.list_box = wx.ListBox(panel, size=(250, 480))
        self.Bind(wx.EVT_LISTBOX, self.on_select, self.list_box)
        self.grid = wx.grid.Grid(panel, size=(390, 480))
        self.grid.CreateGrid(60, 3)
        self.grid.SetColLabelValue(0, "Ability")
        self.grid.SetColLabelValue(1, "Value")
        self.grid.SetColLabelValue(2, "Hex")
        self.grid.SetColSize(0, 150)
        self.grid.SetColSize(1, 75)
        self.grid.SetColSize(2, 75)
        self.grid.HideRowLabels()
        self.search_box = wx.TextCtrl(panel)
        self.search_box.Bind(wx.EVT_TEXT, self.on_key_typed)
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer1.Add(self.search_box)
        sizer1.Add(self.list_box)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer1)
        sizer.Add(self.grid)
        panel.SetSizer(sizer)
        self.players: list[PlayerData] = list()
        self.Bind(wx.EVT_CLOSE, self.on_exit)
        self.on_load()
        self.update_list_box(self.players)


    def on_exit(self, evt: wx.Event):
        self.parent.create_instance()
        evt.Skip()

    def on_load(self):
        reader = DataPacReader(self.file_path)
        try:
            reader.load()
            self.players = reader.read()
        finally:
            reader.close()

    def on_select(self, evt: wx.Event):
        player = self.list_box.GetClientData(self.list_box.GetSelection())
        for i, (ability_name, ability_value) in enumerate(player.data):
            self.grid.SetCellValue(i, 0, ability_name)
            self.grid.SetCellValue(i, 1, str(ability_value))
            self.grid.SetCellValue(i, 2, hex(ability_value))

    def on_key_typed(self, evt: wx.Event):
        search_name = self.search_box.GetValue()
        if search_name:
            self.update_list_box([p for p in self.players if search_name in p.id or search_name in p.name])
        else:
            self.update_list_box(self.players)

    def update_list_box(self, players: list[PlayerData]):
        self.list_box.Clear()
        for player in players:
            self.list_box.Append(f"{player.id}:{player.name}", player)

