from pathlib import Path
from typing import Callable, Type
import wx

from game_data_view import DataViewFrame
from memcard_view import MemcardViewFrame


SIZE = (960, 640)
FRAME_STYLE = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)

class OpenFileFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(OpenFileFrame, self).__init__(*args, **kw, style=FRAME_STYLE)
        panel = wx.Panel(self)
        st = wx.StaticText(panel, label="Drag Me")
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)
        btn = wx.Button(panel, label="Choose File")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(st, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=10)
        sizer.Add(btn, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=10)
        panel.SetSizer(sizer)
        self.setup_menu()
        file_drop_target = WxFileDropTarget(self.on_drag_file)
        self.SetDropTarget(file_drop_target)

    def setup_menu(self):
        menubar = wx.MenuBar()
        menu = wx.Menu()
        menubar.Append(menu, "&File")
        menu.Append(wx.ID_OPEN)
        menu.Append(wx.ID_EXIT)
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.on_open_file, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_CLOSE, self.on_exit)

    def on_open_file(self, evt: wx.Event):
        """
        Open a file dialog to select a PS2 memory card file.
        """

    def on_exit(self, evt: wx.Event):
        self.Destroy()

    def on_drag_file(self, file_paths: list[str]):
        if not file_paths or not file_paths[0]:
            wx.MessageBox("Unsupported file.", "Error", wx.OK | wx.ICON_ERROR)
            return

        path = Path(file_paths[0])
        if not path.is_file():
            wx.MessageBox("Unsupported file.", "Error", wx.OK | wx.ICON_ERROR)
            return

        file_size = path.stat().st_size

        # Check exact matches
        if path.name == "DATA.PAC" and file_size == 778813056:
            self._open_frame(DataViewFrame, file_path=path, parent=self, title="Sakatsuku04 Data Tool")
            return

        # Check suffix match for save files
        if path.suffix == ".ps2":
            self._open_frame(MemcardViewFrame, file_path=path, parent=self, title="Sakatsuku04 Save Tool")
            return

        wx.MessageBox("Unsupported file.", "Error", wx.OK | wx.ICON_ERROR)

    def _open_frame(self, frame_class: Type[wx.Frame], **kwargs):
        """Helper to close current frame and open a new one."""
        self.Close()
        frame = frame_class(None, **kwargs)
        frame.Show()

    @classmethod
    def create_instance(cls):
        frame = cls(None, title="Sakatsuku04 Tool")
        frame.Show()

class WxFileDropTarget(wx.FileDropTarget):
    def __init__(self, call_back: Callable[[list[str]], None]):
        super(WxFileDropTarget, self).__init__()
        self.call_back = call_back

    def OnDropFiles(self, x, y, data: list[str]) -> bool:
        self.call_back(data)
        return True


if __name__ == "__main__":
    app = wx.App()
    OpenFileFrame.create_instance()
    app.MainLoop()