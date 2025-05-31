from pathlib import Path
from typing import Callable, Type
import wx
import wx.adv

from .game_data_view import DataViewFrame
from .memcard_view import MemcardViewFrame
from .version import APP_DISPLAY_NAME, COPY_RIGHT, DESCRIPTION, VERSION


FRAME_STYLE = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)

class OpenFileFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(OpenFileFrame, self).__init__(*args, **kw, style=FRAME_STYLE)
        panel = wx.Panel(self)
        self.create_layout(panel)
        self.setup_menu()
        file_drop_target = WxFileDropTarget(self.on_drag_file)
        self.SetDropTarget(file_drop_target)
        self.bind_events()

    def create_layout(self, panel: wx.Panel):
        st = wx.StaticText(panel, label="Drag Me")
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)
        self.btn = wx.Button(panel, label="Choose File")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(st, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=10)
        sizer.Add(self.btn, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border=10)
        panel.SetSizer(sizer)

    def setup_menu(self):
        menubar = wx.MenuBar()
        menu = wx.Menu()
        menubar.Append(menu, "&File")
        menu.Append(wx.ID_OPEN)
        menu.Append(wx.ID_EXIT)
        help_menu = wx.Menu()
        self.about_item = help_menu.Append(wx.ID_ABOUT, "About", "Show About Page")
        menubar.Append(help_menu, "&Help")
        self.SetMenuBar(menubar)

    def bind_events(self):
        self.Bind(wx.EVT_MENU, self.on_open_file, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_CLOSE, self.on_exit)
        self.Bind(wx.EVT_MENU, self.show_about_dialog, self.about_item)
        self.btn.Bind(wx.EVT_BUTTON, self.on_open_file)

    def show_about_dialog(self, event):
        info = wx.adv.AboutDialogInfo()
        info.SetName(APP_DISPLAY_NAME)
        info.SetVersion(VERSION)
        info.SetDescription(DESCRIPTION)
        info.SetCopyright(COPY_RIGHT)
        # info.SetWebSite("https://yuzhi.tech")
        wx.adv.AboutBox(info)

    def on_open_file(self, evt: wx.Event):
        """
        Open a file dialog to select a PS2 memory card file.
        """
        file_dialog = wx.FileDialog(
            self, "Open", "", "", "PS2 Memory Card Files (*.ps2)|*.ps2", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )
        if file_dialog.ShowModal() == wx.ID_OK:
            self._open_frame(MemcardViewFrame, file_path=file_dialog.GetPath(), parent=self, title="Sakatsuku04 Save Editor")
            file_dialog.Destroy()

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
        if not frame.error:
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


def main():
    app = wx.App()
    OpenFileFrame.create_instance()
    app.MainLoop()


if __name__ == "__main__":
    main()
