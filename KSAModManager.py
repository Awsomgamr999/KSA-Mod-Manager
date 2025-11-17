import os
import zipfile
import tempfile
import shutil
import tomllib
import tomli_w
import requests
import sys
import ssl
import certifi
import subprocess
import time
from urllib.request import urlopen, Request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.toml")
MOD_SETUP_FOLDER = os.path.join(SCRIPT_DIR, "ModSetup")
KSAMM_FILE = "ksamm.toml"
KSAMM_VERSION = "v0.1.3"

ssl_context = ssl.create_default_context(cafile=certifi.where())

def get_install_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def check_for_updates():
    print("Checking for updates...")
    try:
        req = Request(GITHUB_RELEASES_API)
        with urlopen(req, context=ssl_context) as r:
            import json
            data = json.load(r)
        latest = data.get("tag_name")
        assets = data.get("assets", [])
        if not latest or not assets:
            print("Invalid GitHub release format.")
            return None, None
        download_url = assets[0].get("browser_download_url")
        if latest == KSAMM_VERSION:
            print(f"You already have the latest version ({KSAMM_VERSION}).")
            return latest, None
        print(f"New version available: {latest}")
        return latest, download_url
    except Exception as e:
        print("Update check failed:", e)
        return None, None

def install_update(download_url):
    print("\nDownloading update...")
    tmp_zip = os.path.join(tempfile.gettempdir(), "ksam_update.zip")
    try:
        req = Request(download_url)
        with urlopen(req, context=ssl_context) as r:
            with open(tmp_zip, "wb") as f:
                f.write(r.read())
    except Exception as e:
        print("Failed to download update:", e)
        return
    print("Download complete.\nExtracting update...")
    extract_dir = os.path.join(tempfile.gettempdir(), "ksam_update_extract")
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(tmp_zip, 'r') as z:
        z.extractall(extract_dir)
    print("Update extracted.")
    # Launch UpdateHelper.exe
    install_dir = get_install_dir()
    updater_path = os.path.join(install_dir, "UpdateHelper.exe")
    if not os.path.exists(updater_path):
        print("ERROR: UpdateHelper.exe not found next to KSAMMModManager.exe")
        return
    print("Starting updater...")
    subprocess.Popen([updater_path, extract_dir, install_dir])
    sys.exit(0)


def save_paths(game_data, game_files):
    data = {
        "paths": {
            "GameData": game_data,
            "GameFiles": game_files
        }
    }
    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(data, f)
        
    print("Paths saved!")


def load_paths():
    if not os.path.exists(CONFIG_FILE):
        print("No paths saved yet.")
        return None, None

    try:
        with open (CONFIG_FILE, "rb") as f:
            data = tomllib.load(f)

        paths = data.get("paths", {})
        game_data = paths.get("GameData")
        game_files = paths.get("GameFiles")

        if not game_data or not game_files:
            print("Missing at least one path entry.")
            return None, None

        return game_data, game_files

    except Exception as e:
        print("Error:", e)
        return None, None


def require_kitten_path(path_name):
    # Forces the user to enter a path ending in 'Kitten Space Agency'
    while True:
        p = input(f"Enter the {path_name} path: ").strip()
        if os.path.basename(p) == "Kitten Space Agency":
            return p
        print("ERROR: The final folder must be 'Kitten Space Agency'.")


def read_mod_name(mod_toml_path):
    # Extract the name from a mod.toml file.
    if not os.path.exists(mod_toml_path):
        return None

    try:
        with open(mod_toml_path, "rb") as f:
            data = tomllib.load(f)

        return data.get("name", None)

    except Exception as e:
        print("Error:", e)
        return None
    return None


def rebuild_manifest(manifest_path, game_path):
    # Rebuild manifest.toml, makes sure to keep Core.
    content_path = os.path.join(game_path, "Content")
    manifest_file = os.path.join(manifest_path, "manifest.toml")

    if not os.path.isdir(content_path):
        print("No Content folder found.")
        return
        
    entries = []
    core_entry = None

    for folder in os.listdir(content_path):
        mod_dir = os.path.join(content_path, folder)
        mod_toml = os.path.join(mod_dir, "mod.toml")

        if not os.path.exists(mod_toml):
            continue

        mod_name = read_mod_name(mod_toml)
        if not mod_name:
            continue

        entry = {
            "id": mod_name,
            "enabled": True
        }

        if folder.lower() == "core":
            core_entry = entry  # store but don't append yet
        else:
            entries.append(entry)

    # Write Core first
    final_entries = []
    if core_entry:
        final_entries.append(core_entry)
    else:
        print("WARNING: Core mod missing from Content!")

    # Write all normal mods after Core
    final_entries.extend(entries)

    data = {"mods": final_entries}
    with open(manifest_file, "wb") as f:
        tomli_w.dump(data, f)

    print("manifest.toml rebuilt.")


def install_mods(manifest_path, game_path):
    content_path = os.path.join(game_path, "Content")
    os.makedirs(content_path, exist_ok=True)

    if not os.path.exists(MOD_SETUP_FOLDER):
        print("No ModSetup folder found.")
        return

    zips = [z for z in os.listdir(MOD_SETUP_FOLDER) if z.endswith(".zip")]

    if not zips:
        print("No .zip mods found in ModSetup/")
        return

    for zip_file in zips:
        zip_path = os.path.join(MOD_SETUP_FOLDER, zip_file)

        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(content_path)
            print(f"Installed {zip_file}")

        # remove zip after success
        os.remove(zip_path)

    print("All mods installed. Rebuilding manifest...")
    rebuild_manifest(manifest_path, game_path)


def manage_mods(manifest_path, game_path):
    content_path = os.path.join(game_path, "Content")

    while True:
        mods = []
        for folder in os.listdir(content_path):
            if folder.lower() == "core":
                continue

            mod_toml = os.path.join(content_path, folder, "mod.toml")
            if os.path.exists(mod_toml):
                mod_name = read_mod_name(mod_toml)
                if mod_name:
                    mods.append((folder, mod_name))

        if not mods:
            print("No installed mods found.")
            return

        print("\nInstalled Mods:")
        for idx, (folder, mod_name) in enumerate(mods, start=1):
            print(f"{idx}. {mod_name} ({folder})")

        choice = input("Enter number to delete, or 'q' to quit: ")

        if choice.lower() == "q":
            return

        if not choice.isdigit() or not (1 <= int(choice) <= len(mods)):
            print("Invalid choice.")
            continue

        idx = int(choice) - 1
        folder, mod_name = mods[idx]
        mod_path = os.path.join(content_path, folder)

        # delete folder
        shutil.rmtree(mod_path)
        print(f"Deleted {mod_name}.")

        # update manifest
        print("Updating manifest...")
        rebuild_manifest(manifest_path, game_path)


def check_for_dependencies(game_path):
    content_path = os.path.join(game_path, "Content")
    if not os.path.isdir(content_path):
        print("No Content folder found.")
        return

    mod_folders = [f for f in os.listdir(content_path) if os.path.isdir(os.path.join(content_path, f))]
    if not mod_folders:
        print("No mod folders found in Content/.")
        return

    # Installed mod names
    installed_mods = set()
    for folder in mod_folders:
        mod_toml = os.path.join(content_path, folder, "mod.toml")
        if os.path.exists(mod_toml):
            mod_name = read_mod_name(mod_toml)
            if mod_name:
                installed_mods.add(mod_name.lower())

    any_missing = False  # Track if there are any missing deps overall

    for folder in mod_folders:
        ksamm_toml = os.path.join(content_path, folder, KSAMM_FILE)
        if not os.path.exists(ksamm_toml):
            continue

        try:
            with open(ksamm_toml, "rb") as f:
                data = tomllib.load(f)

            missing_required = {}
            missing_optional = {}

            for key in ("dependencies", "optional_dependencies"):
                dep_list = data.get(key, [])
                if not isinstance(dep_list, list):
                    continue
                for dep in dep_list:
                    if not isinstance(dep, dict):
                        continue
                    dep_name = dep.get("name", "").strip()
                    dep_link = dep.get("link", "").strip()
                    if not dep_name:
                        continue
                    if dep_name.lower() not in installed_mods:
                        if key == "dependencies":
                            missing_required[dep_name] = dep_link
                        else:
                            missing_optional[dep_name] = dep_link

            # Print missing dependencies for this mod
            if missing_required or missing_optional:
                any_missing = True
                print(f"\nMod: {folder}\n")
                print("You Have Missing Dependencies!\n")

                if missing_required:
                    print("  Required:\n")
                    for name, link in missing_required.items():
                        print(f'    - "{name}" | "{link}"\n')

                if missing_optional:
                    print("  Optional:\n")
                    for name, link in missing_optional.items():
                        print(f'    - "{name}" | "{link}"\n')

        except Exception as e:
            print(f"Error reading {ksamm_toml}: {e}")

    if not any_missing:
        print("No missing dependencies found.")

# Info
print("ModManager created by Awsomgamr999.\nProtected by CC-BY-NC-SA\nYou are free to modify and release a version of this tool, so long as you credit me and don't use it for commercial purposes.")

def main():
    while True:
        print("\n=== Mod Installer ===")
        print("1. Set paths")
        print("2. Install mods")
        print("3. Manage installed mods")
        print("4. Check for updates")
        print("q. Quit")

        choice = input("Choose an option: ")

        if choice == "1":
            manifest = require_kitten_path("manifest")
            game = require_kitten_path("game")
            save_paths(manifest, game)

        elif choice == "2":
            manifest, game = load_paths()
            if manifest and game:
                install_mods(manifest, game)
                check_for_dependencies(game)

        elif choice == "3":
            manifest, game = load_paths()
            if manifest and game:
                manage_mods(manifest, game)
                
        elif choice == "4":
            latest, url = check_for_updates()
            if not latest:
                print("Unable to check updates.")
                continue

            if latest == KSAMM_VERSION:
                print("You already have the latest version.")
                continue

            ask = input("Install now? (y/n): ").lower()

            if ask == "y":
                install_update(url)

        elif choice.lower() == "q":
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()







