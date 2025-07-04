import tomllib
import PyInstaller.__main__
from pathlib import Path
import platform

if platform.system() == "Darwin":
    icon_path = "assets/app.icns"
else:
    icon_path = "assets/app.ico"

config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

pyi_cfg = config["tool"]["pyinstaller"]

PyInstaller.__main__.run([
    f"--name={pyi_cfg['app_name']}",
    "--windowed" if pyi_cfg.get("windowed") else "",
    "--onefile" if pyi_cfg.get("onefile") else "",
    f"--icon={icon_path}" if icon_path else "",
    *[f"--add-data={d}" for d in pyi_cfg["add_data"]],
    pyi_cfg["entry_point"]
])
