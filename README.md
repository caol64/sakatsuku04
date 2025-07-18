# Sakatsuku04 editor

![](data/cover.jpg)

Opensource game and save editor for J.League Pro Soccer Club o Tsukurou! 04 (PS2).

## Quick Start

The recommended way to run `Saka04Editor` is by using [`uv`](https://github.com/astral-sh/uv) to create and manage a virtual environment:

```bash
uv venv --python python3.13
uv pip install Saka04Editor
uv run Saka04Editor
```

Alternatively, you can download the latest prebuilt releases from GitHub:
👉 [https://github.com/caol64/sakatsuku04/releases](https://github.com/caol64/sakatsuku04/releases)

## Features

Currently supported viewing features:

* Club information

  * Club name
  * Funds
  * Game year, month, date
  * Manager name
  * Game difficulty
* My Team information

  * Player basic information (name, age, birthplace, rank, growth types, cooperation types, tone types, play styles)
  * Player abilities
* Other team information

  * Teams (name, friendliness) and players (name, age, rank, growth types, cooperation types, tone types)
* Scout

  * My Scout abilities

Currently supported editing features:

* Club information

  * Funds
  * Game year
  * Game difficulty
* My Team information

  * Player basic information (age, birthplace, growth types, cooperation types, tone types, play styles)
  * Player abilities
* Other team information

  * Teams (friendliness)
* **Real-time modification**

  * Modify game data on a connected PCSX2 emulator in real time with the same capabilities as current save file editing.

## Screenshots

![](data/5.png)

![](data/6.png)

![](data/7.png)

## Hacker notes

[Save File Format Analysis](docs/save_file_format_analysis.md)

## Acknowledgements

The data used in this project was obtained from \[サカつく04緑本追補] and \[サカつく04データ置き場]. I am grateful for their contribution to making this information publicly available.

## References

* [サカつく04緑本追補](https://sites.google.com/view/sakatsuku04/home)
* [サカつく04データ置き場](https://www.potato.ne.jp/ando/sakatuku/index.html)
