# KSA Mod Manager

Created by Awsomgamr999
Protected under CC-BY-NC-SA

NOTE: The following instructions are for the build that is compiled into a .exe, you will have to do that yourself if you get it from GitHub.

## Changelog:

## 0.1.0:
- Initial Build
## 0.1.1:
- paths.txt has been replaced with config.toml
- Developers can now include a `ksamm.toml` file in their mod for configurations in the KSA Mod Loader. Currently you can specify required and optional dependencies. see [ksamm_toml information](https://github.com/Awsomgamr999/KSA-Mod-Manager/blob/main/docs/ksamm_toml.md) for instructions on how to format it.
- Added a `docs` folder which gives detailed information on the uses of KSAMM.

## Quickstart Guide:
1. Run KSAModManager.exe
2. Select "1" to specify your Manifest and Content\ paths. Please only go to the "Kitten
    Space Agency" folder, the program will handle the rest.
3. Put zips of mods in the "ModSetup" folder.
4. Select "2" to install mods.
5. Your KSA is now set up. If you ever want to remove a mod use "3" and select the mods that
    you want to delete.

NOTE: This is NOT a modloader. Please also have StarMap installed if you want to use a code
    mod, this can be used to put the mod in the right place but you need StarMap to actually inject code.

## Planned Features:
- Auto-Install for mod dependencies
- Better mod management, where you can disable & re-enable mods later
- Auto-update for mods
- Auto-update for KSAMM
- Eventually a mod search tool to find new mods

## Troubleshooting:
- If for some reason its erroring when installing mods, please either run it as Administrator or change permissions to allow users to modify your KSA directory. (I dont think it will be an issue as its a .exe now but just in case.)

Thank you for downloading ModManager!

If you have any issues please ping me on either the main KSA Discord or the KSA Modding
    Society Discord.
