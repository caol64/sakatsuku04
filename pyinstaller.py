# pyinstaller.py
import os
import PyInstaller.__main__

from version import APP_NAME

app_name = APP_NAME
app_file = 'src/main_frame.py'
# hidden_import = 'glcontext'
datas = ['resource', 'resource']

PyInstaller.__main__.run(
    [
        '--name=%s' % app_name,
        '--windowed',
        '--onefile',
        #'--icon=%s' % 'path/to/your/icon.ico',
        '--add-data=%s' % os.pathsep.join(datas),
        # '--hidden-import=%s' % hidden_import,
        app_file,
    ]
)
