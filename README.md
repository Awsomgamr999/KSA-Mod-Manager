# KSA Mod Manager

Copyright © 2025 Awsomgamr999

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


> Version: 0.1.5a

### NOTE: 
- All mods are downloaded and used at your own risk. You are responsible for any damage, data loss, or security issues caused by third-party mods. Always review source code and be cautious about what you run.
- I encourage you to look through the source code yourself, or at least have AI to do it. This program is safe but this early into KSA there is not really a team validating the safety of mods and tools for KSA. Looking through and verifying that this code is safe gets you into the habit of verifying before you accidentally install a virus or something.

Zipped MD5 checksum: `937aea6c4bd15ef543974d1cf70254f2` Read about [Checksums](https://en.wikipedia.org/wiki/Checksum).

## Changelog:

## 0.1.0:
- Initial Build
## 0.1.1:
- paths.txt has been replaced with config.toml
- Developers can now include a `ksamm.toml` file in their mod for configurations in the KSA Mod Loader. Currently you can specify required and optional dependencies. see [ksamm_toml information](https://github.com/Awsomgamr999/KSA-Mod-Manager/blob/main/docs/ksamm_toml.md) for instructions on how to format it.
- Added a `docs` folder which gives detailed information on the uses of KSAMM.
- In the spirit of a project being open code, the download link has been changed to be on GitHub and the original `KSAModLoader.py` also downloads with the rest of the tool. It is still easiest to run using the `KSAModLoader.exe`.
- The folder that contains the actual program is now `KSAMM/`
## 0.1.2
- Adds new selection, "4" that will check for and allow you to install updates for KSAMM.
## 0.1.3
- Adds support for using StarMap (idk how I forgot this before sorry y'all)
- You can now launch the game from KSAMM. If you have a Mod Loader (StarMap) configured and specify it's path when prompted it will use the Mod Loader, otherwise it will boot the base game.
- Bug fixes to UpdateHelper.exe
- Changed license to MIT
## 0.1.4
- Added the ability for modders to specify metadata.
- Updated the visuals. (Still in a command prompt)
- Specified `[dependencies]` within ksamm.toml now auto install as long as correct information is given.
- `set paths` now has an otion to automatically look for paths.
## 0.1.5
- Hotfix for critical issues in 0.1.4
- Added a check for BOM data to make KSAMM `toml` reading more robust. Check out information on [Byte Order Marks](https://en.wikipedia.org/wiki/Byte_order_mark) here.
## 0.1.5a
- Hotfix for critical issues in 0.1.5
- Mod developer metadata in `ksamm.toml` has been unlocked. You can now specify any metadata that you see fit and it will appear.
- LICENSE.txt has been repackaged into `KSAModManager.zip`. It was forgotten in the previous release.

## Quickstart Guide:
1. Run KSAModManager.exe
2. Select "1" to specify your Manifest and Content\ paths. Select 2 for automatic searching and 1 for manual entering of directories. In the case of main game files, please only go to the "Kitten
    Space Agency" folder, the program will handle the rest.
3. Put zips of mods in the "ModSetup" folder.
4. Select "2" to install mods.
5. Your KSA is now set up. If you ever want to remove a mod use "3" and select the mods that
    you want to delete.

NOTE: This is NOT a modloader. Please also have StarMap installed if you want to use a code
    mod, this can be used to put the mod in the right place but you need StarMap to actually inject code.

## Planned Features:
- Better mod management, where you can disable & re-enable mods later
- Auto-update for mods
- Eventually a mod search tool to find new mods

## Troubleshooting:
### WARNING: FOLLOW ALL INSTRUCTIONS EXACTLY
- KSAMM is erroring about permissions when I try to install mods.
    - Reason
        - KSA by default installs in `C:\Program Files\`, this is a protected folder and as such by default KSA is also protected. KSAMM cannot modify this without express permission.
    - Solution(s)
        - Solution 1:
            - Every time you run KSAMM, right click the .exe and select, "Run as Administrator".
        - Solution 2:
            - Navigate to your `C:\Program Files\`
            - Right-click on `Kitten Space Agency\`
            - Click `Properties`
            - Click `Security`
            - Click `Edit...`
            - Click `Users` in the Group or user names section of the popup
            - Click the `Allow` under `Modify`
            - Click `Apply`
    - After following these steps KSAMM should have necessary permissions.
 
- I have some other issue
    - Please ping me on Discord with more information.

Thank you for downloading ModManager!

If you have any issues please ping me on either the main KSA Discord or the KSA Modding Society Discord.
