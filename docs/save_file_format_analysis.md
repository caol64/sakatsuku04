# Save File Format Analysis

## Save File Directory

After exporting the game save, the file directory is as follows:

```
BISLPM-65530Saka_G03
├── BISLPM-65530Saka_G03
├── head.dat
├── icon.sys
├── mc_main_1.ico
├── mc_main_2.ico
└── mc_main_3.ico
```

The directory name is `BISLPM-65530Saka_G` followed by a number. If there are multiple records on the same memory card, the number will start from `01` and increment.

The `BISLPM-65530Saka_G03` file is the main save file, containing all the game data. It is compressed using `Bit-Packing` technology and encrypted with the `BlowFish` algorithm.

The `head.dat` file stores some basic game information, such as the club name and the date in the game. It is not compressed or encrypted.

The `icon.sys` and the three `mc_main_x.ico` files are the 3D icons for the save, which I introduced in a previous article. [Link](https://babyno.top/en/posts/2023/10/parsing-ps2-3d-icon/)

## File Structure

`BISLPM-65530Saka_G03` and `head.dat` have the same file structure, as shown in the figure below:

![](https://babyno.top/imgs/posts/2025-01-14-sakatsuku-04-game-reverse-save-file-analysis/saka_tool.jpg)

Each file is divided into four parts: `Header`, `Data Block1`, `CRC`, and `Data Block2`.

The first 4 bytes of the file are the `Header`, from which the total size of the `Data Block` can be extracted. Based on this size, the specific positions of `Data Block1`, `CRC`, and `Data Block2` can be calculated. Finally, concatenating `Data Block1` and `Data Block2` will give the complete data.

Taking `head.dat` as an example:

![](https://babyno.top/imgs/posts/2025-01-14-sakatsuku-04-game-reverse-save-file-analysis/2.jpg)

The dark parts in the figure are the `Header` and `CRC`, and the two white parts are `Data Block1` and `Data Block2`.
