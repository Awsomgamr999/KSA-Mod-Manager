# Imports
import os, sys, time, zipfile, tempfile, shutil, subprocess, tomllib, tomli_w, ssl, certifi, json, requests, io
from urllib.request import urlopen, Request

# Current directory for KSAMM
if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
elif __file__:
    SCRIPT_DIR = os.path.dirname(__file__)

# Some kinda important variables
CONFIG_FILE = os.path.join(SCRIPT_DIR + "\\config.toml")
MOD_SETUP_FOLDER = os.path.join(SCRIPT_DIR, "ModSetup")
KSAMM_FILE = "ksamm.toml"
KSAMM_VERSION = "0.1.7"
GITHUB_RELEASES_API = "https://api.github.com/repos/Awsomgamr999/KSA-Mod-Manager/releases/latest"
SPACEDOCK_DOWNLOAD = "https://spacedock.info/mod/4048/KSA%20Mod%20Manager%20(KSAMM)/download"
mod_loader_candidates = ["StarMap.exe", "Ksaloader.exe"]
STARMAP_DOWNLOAD = "https://api.github.com/repos/StarMapLoader/StarMap/releases/latest"

ssl_context = ssl.create_default_context(cafile=certifi.where())

class Ledger:

    # colors
    RESET   = "\033[0m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    RED     = "\033[91m"
    YELLOW  = "\033[93m"
    BOLD    = "\033[1m"

    def __init__(self, width=60):
        self.width = width
        self.line = "─" * self.width

    def header(self, title: str):
        print(self.CYAN + self.line)
        print(f"{self.BOLD}{self.CYAN}  {title}{self.RESET}")
        print(self.CYAN + self.line + self.RESET)

    def heading(self, title: str):
        print(f"\n{self.BOLD}{self.YELLOW}{title}{self.RESET}")

    def block(self, entries: dict):
        if entries:
            max_len = max(len(str(k)) for k in entries.keys())
            for key, value in entries.items():
                print(f"  {key:<{max_len}} : {value}")
        else:
            print("  (none)")

    def info(self, message: str):
        print(f"{self.CYAN}  {message}{self.RESET}")

    def success(self, message: str):
        print(f"{self.GREEN}  OK    : {message}{self.RESET}")

    def error(self, message: str):
        print(f"{self.RED}  ERROR : {message}{self.RESET}")

ledger = Ledger()

# ===================== Initialization =====================
def initialize():
    ledger.header(f"Kitten Space Agency Mod Manager {KSAMM_VERSION}")
    ledger.info("Checking required folders and config files...")
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            f.write('[paths]\nManifestPath = ""\nGamePath = ""\nModLoaderPath = ""\nModLoaderVersion = ""\nDependencyAllowList = []')
    if not os.path.exists(MOD_SETUP_FOLDER):
        os.mkdir(MOD_SETUP_FOLDER)
    ledger.success("Initialization complete.")
    startup_update_warn()

# ===================== Path Management =====================
def require_kitten_path(name, prompt, required_exes=None):
    while True:
        user_in = input(f"{prompt} ")
        if user_in.lower() == "cancel":
            return None
        if not os.path.exists(user_in):
            ledger.error("Path does not exist.")
            continue
        if required_exes:
            found = any(os.path.isfile(os.path.join(user_in, exe)) for exe in required_exes)
            if not found:
                ledger.error(f"Path missing required file(s): {', '.join(required_exes)}")
                continue
        return os.path.abspath(user_in)

def save_paths(manifest_path, game_path, mod_loader_path, mod_loader_version, allowlist):
    with open(CONFIG_FILE, "rb") as f:
        existing_data = tomllib.load(f)

    paths = existing_data.get("paths", {})

    old_manifest_path = paths.get("ManifestPath")
    old_game_path = paths.get("GamePath")
    old_mod_loader_path = paths.get("ModLoaderPath")
    old_mod_loader_version = paths.get("ModLoaderVersion")
    old_dependency_allow_list = paths.get("DependencyAllowList", [])
    manifest_path = manifest_path or old_manifest_path or ""
    game_path = game_path or old_game_path or ""
    mod_loader_path = mod_loader_path or old_mod_loader_path or ""
    mod_loader_version = mod_loader_version or old_mod_loader_version or ""
    allowlist = allowlist or old_dependency_allow_list or []
    data = {"paths": {
        "ManifestPath": manifest_path or "",
        "GamePath": game_path or "",
        "ModLoaderPath": mod_loader_path or "",
        "ModLoaderVersion": mod_loader_version or "",
        "DependencyAllowList": allowlist or []
    }}
    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(data, f)
    ledger.success("Paths saved!")

def load_paths():
    if not os.path.exists(CONFIG_FILE):
        ledger.error("No paths saved yet.")
        return None, None, None, None, []
    try:
        with open(CONFIG_FILE, "rb") as f:
            data = tomllib.load(f)
        paths = data.get("paths", {})
        return paths.get("ManifestPath"), paths.get("GamePath"), paths.get("ModLoaderPath"), paths.get("ModLoaderVersion"), paths.get("DependencyAllowList", [])
    except Exception as e:
        ledger.error(f"Error reading config: {e}")
        return None, None, None, None, []
    
def find_paths():
    ledger.heading("Attempting to find paths.")
    user_docs = os.path.expanduser("~\\Documents")
    one_drive_docs = os.path.expanduser("~\\OneDrive\\Documents")

    common_manifest_roots = [
        os.path.join(user_docs, "My Games", "Kitten Space Agency"),
        os.path.join(user_docs, "Kitten Space Agency"),
        os.path.join(one_drive_docs, "My Games", "Kitten Space Agency"),
        os.path.join(one_drive_docs, "Kitten Space Agency")
    ]
    program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    desktop_onedrive_dir = os.path.expanduser("~\\OneDrive\\Desktop")
    default_install_path = os.path.join(os.getcwd(), "StarMap")
    desktop_dir = os.path.expanduser("~\\Desktop")
    common_game_roots = [
        os.path.join(program_files, "Kitten Space Agency"),
    ]

    mod_loader_candidates = ["StarMap.exe", "Ksaloader.exe"]

    manifest_path = None
    game_path = None
    mod_loader_path = None
    mod_loader_version = None
    allowlist = None

    for root in common_manifest_roots:
        candidate = os.path.join(root, "manifest.toml")
        if os.path.isfile(candidate):
            manifest_path = candidate
            ledger.success(f"Found manifest: {manifest_path}")
            manifest_path = os.path.dirname(manifest_path)
            manifest_path = os.path.join(manifest_path, "manifest.toml")
            break

    if not manifest_path:
        ledger.error("Manifest.toml not found in common locations.")

    for root in common_game_roots:
        exe_path = os.path.join(root, "KSA.exe")
        if os.path.isfile(exe_path):
            game_path = root
            ledger.success(f"Found game directory: {game_path}")
            break

    if not game_path:
        for root_dir in [program_files, program_files_x86]:
            ledger.info(f"Game not found in common locations, searching under {root_dir}...")
            for root, dirs, files in os.walk(root_dir):
                if "KSA.exe" in files:
                    game_path = root
                    ledger.success(f"Found game directory: {game_path}")
                    break
            if game_path:
                break

    if not game_path:
        ledger.error("KSA.exe not found.")

    for root in common_game_roots:
        for exe in mod_loader_candidates:
            candidate = os.path.join(root, exe)
            if os.path.isfile(candidate):
                mod_loader_path = root
                ledger.success(f"Found mod loader directory: {mod_loader_path}")
                break
        if mod_loader_path:
            break

    if not mod_loader_path:
        for root_dir in [program_files, program_files_x86, desktop_dir, desktop_onedrive_dir, default_install_path]:
            ledger.info(f"Mod loader not found in common locations, searching under {root_dir}...")
            for root, dirs, files in os.walk(root_dir):
                if any(exe in files for exe in mod_loader_candidates):
                    mod_loader_path = root
                    ledger.success(f"Found mod loader directory: {mod_loader_path}")
                    break
            if mod_loader_path:
                break

    if mod_loader_path is None:
        choice = input("Mod loader (StarMap/Ksaloader) not found. Do you have it installed? (y/n): ").lower()
        if choice == "y":
            mod_loader_path = require_kitten_path(
                "Mod Loader", "Enter mod loader directory (or cancel):", mod_loader_candidates
            )
        else:
            installChoice = input("Would you like to install the latest version of StarMap? (y/n)").lower()
            if installChoice == "y":
                try:
                    ledger.info("Installing the latest version of StarMap...")

                    # Fetch GitHub release info
                    response = requests.get(STARMAP_DOWNLOAD)
                    response.raise_for_status()
                    latest_release = response.json()
                    mod_loader_version = latest_release.get("tag_name")

                    # Find the .zip asset
                    zip_asset = next((a for a in latest_release["assets"] if a["name"].endswith(".zip")), None)
                    if not zip_asset:
                        ledger.error("No .zip release found!")
                        exit(1)

                    zip_url = zip_asset["browser_download_url"]
                    ledger.info(f"Downloading {zip_asset['name']}...")

                    r = requests.get(zip_url)
                    r.raise_for_status()
                    z = zipfile.ZipFile(io.BytesIO(r.content))

                    # Install path
                    install_path = os.path.join(os.getcwd(), "StarMap")
                    os.makedirs(install_path, exist_ok=True)
                    z.extractall(install_path)
                    ledger.info(f"StarMap installed to {install_path}")

                    # Configure StarMap JSON
                    starmap_config_path = os.path.join(install_path, "StarMapConfig.json")
                    config_data = {
                        "GameLocation": game_path,
                        "RepositoryLocation": ""
                    }
                    with open(starmap_config_path, "w", encoding="utf-8") as f:
                        json.dump(config_data, f, indent=4)
                    ledger.info(f"StarMap automatically configured! Config saved at {starmap_config_path}")

                    # Update mod_loader_path to point to StarMap install
                    mod_loader_path = install_path

                    # Save paths + version
                    save_paths(manifest_path, game_path, mod_loader_path, mod_loader_version, allowlist)
                    ledger.info("Paths and version saved to KSAMM config.")

                except Exception as e:
                    ledger.error(f"Error installing StarMap: {e}")

            else:
                ledger.info("Mod loader will be left unset (optional).")

    return manifest_path, game_path, mod_loader_path, mod_loader_version, allowlist

# ===================== Mod Management =====================
def strip_bom_and_get_text(file_path, ledger):
    
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            text_data = f.read()

        text_data = text_data.replace('\r', '')     
        
        text_data = text_data.replace('\ufeff', '')
        
        text_data = text_data.strip() 

        if not text_data:
             ledger.warning(f"{file_path} resulted in empty content after stripping. Skipping rewrite.")
             return None

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_data)
        
        return text_data

    except UnicodeDecodeError as e:
        ledger.error(f"Failed to decode {file_path}. It might not be a standard text format: {e}")
        return None
    except Exception as e:
        ledger.error(f"An unexpected error occurred during file stripping/rewrite for {file_path}: {e}")
        return None
    
def read_mod_name(file_path, ledger):
    if not os.path.exists(file_path):
        ledger.error(f"TOML file missing: {file_path}")
        return None
    
    toml_text = strip_bom_and_get_text(file_path, ledger)
    
    if toml_text is None:
        return None

    try:
        data = tomllib.loads(toml_text)
        
        mod_name = data.get("name")
        return mod_name
        
    except tomllib.TOMLDecodeError as e:
        ledger.error(f"Error decoding TOML in {file_path}: {e}")
        return None
    except Exception as e:
        ledger.error(f"An unexpected error occurred while processing TOML in {file_path}: {e}")
        return None


def rebuild_manifest(manifest_path, game_path):
    content_path = os.path.join(game_path, "Content")
    manifest_file = manifest_path
    if not os.path.isdir(content_path):
        ledger.error("No Content folder found.")
        return
    entries = []
    core_entry = None
    for folder in os.listdir(content_path):
        mod_dir = os.path.join(content_path, folder)
        mod_toml = os.path.join(mod_dir, "mod.toml")
        if not os.path.exists(mod_toml):
            continue
        mod_name = read_mod_name(mod_toml, ledger)
        if not mod_name:
            continue
        entry = {"id": mod_name, "enabled": True}
        if folder.lower() == "core":
            core_entry = entry
        else:
            entries.append(entry)
    final_entries = [core_entry] if core_entry else []
    final_entries.extend(entries)
    with open(manifest_file, "wb") as f:
        tomli_w.dump({"mods": final_entries}, f)
    ledger.success("manifest.toml rebuilt.")

def install_mods(manifest_path, game_path):
    content_path = os.path.join(game_path, "Content")
    os.makedirs(content_path, exist_ok=True)
    if not os.path.exists(MOD_SETUP_FOLDER):
        ledger.error("No ModSetup folder found.")
        return
    zips = [z for z in os.listdir(MOD_SETUP_FOLDER) if z.endswith(".zip")]
    if not zips:
        ledger.error("No .zip mods found in ModSetup folder.")
        return
    for zip_file in zips:
        zip_path = os.path.join(MOD_SETUP_FOLDER, zip_file)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(content_path)
            ledger.success(f"Installed {zip_file}")
        os.remove(zip_path)
    rebuild_manifest(manifest_path, game_path)

def manage_mods(manifest_path, game_path):
    content_path = os.path.join(game_path, "Content")
    while True:
        mods = [(folder, read_mod_name(os.path.join(content_path, folder, "mod.toml"), ledger))
                for folder in os.listdir(content_path)
                if folder.lower() != "core" and os.path.exists(os.path.join(content_path, folder, "mod.toml"))]
        mods = [m for m in mods if m[1]]
        if not mods:
            ledger.error("No installed mods found.")
            return
        ledger.heading("Installed Mods")
        ledger.block({str(i+1): f"{m[1]} ({m[0]})" for i, m in enumerate(mods)})
        choice = input("Enter number to delete, or 'q' to quit: ")
        if choice.lower() == "q":
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(mods)):
            ledger.error("Invalid choice.")
            continue
        idx = int(choice)-1
        folder, mod_name = mods[idx]
        shutil.rmtree(os.path.join(content_path, folder))
        ledger.success(f"Deleted {mod_name}")
        rebuild_manifest(manifest_path, game_path)

# ===================== Metadata =====================

def check_for_metadata(manifest, game_path, allowlist, mode="metadata"):
    content_path = os.path.join(game_path, "Content")
    if not os.path.isdir(content_path):
        ledger.error("No Content folder found.")
        return

    mod_folders = [f for f in os.listdir(content_path) if os.path.isdir(os.path.join(content_path, f))]
    installed_mods = {}
    
    for f in mod_folders:
        mod_toml_path = os.path.join(content_path, f, "mod.toml")
        if not os.path.exists(mod_toml_path):
            continue
        mod_name = read_mod_name(mod_toml_path, ledger)
        if mod_name:
            installed_mods[mod_name.lower()] = f

    any_missing = False
    
    for folder in mod_folders:
        ksamm_toml = os.path.join(content_path, folder, KSAMM_FILE)
        if not os.path.exists(ksamm_toml):
            continue
            
        toml_text = None
        data = None

        try:
            toml_text = strip_bom_and_get_text(ksamm_toml, ledger)
            
            if toml_text is None:
                ledger.error(f"Failed to read/strip BOM from {ksamm_toml}. Skipping.")
                continue
            
            try:
                data = tomllib.loads(toml_text)
            except tomllib.TOMLDecodeError as e:
                ledger.error(f"TOML syntax error in {ksamm_toml}: {e}")
                continue 
            missing_required = {}
            missing_optional = {}
            for key in ("dependencies", "optional_dependencies"):
                dep_list = data.get(key, [])
                if isinstance(dep_list, list):
                    for dep in dep_list:
                        if isinstance(dep, dict):
                            dep_name = dep.get("name", "").strip()
                            dep_link = dep.get("link", "").strip()
                            if dep_name and mode == "dependencies":
                                if dep_name.lower() not in installed_mods:
                                    ledger.info(f"Missing dependency detected: {dep_name} ({key})")
                                    if key == "dependencies":
                                        missing_required[dep_name] = dep_link
                                    else:
                                        missing_optional[dep_name] = dep_link

            if mode == "dependencies" and (missing_required or missing_optional):
                any_missing = True
                ledger.heading(f"Missing dependencies for {folder}")
                ledger.block({"Required": list(missing_required.keys()), "Optional": list(missing_optional.keys())})
                install_dependencies(game_path, manifest, allowlist)

            if mode == "metadata":
                
                raw_meta = data.get("metadata", {})
                
                if not isinstance(raw_meta, dict):
                    ledger.error(
                        f"TOML key 'metadata' in {ksamm_toml} is expected to be a table ({{...}}), "
                        f"but found type {type(raw_meta).__name__}. Skipping metadata display for this mod."
                    )
                    meta_to_display = {}
                else:
                    meta_to_display = {}
                    
                    for key, value in raw_meta.items():
                        display_key = key.replace('_', ' ').title()
                        
                        meta_to_display[display_key] = str(value)
                
                ledger.heading(f"Metadata for {folder}")
                ledger.block(meta_to_display)
                
        except UnicodeDecodeError as e:
            ledger.error(f"Character encoding error in {ksamm_toml}: {e}")
            continue
            
        except Exception as e:
            ledger.error(f"Error processing file {ksamm_toml}: {e}")
            continue
            
    if mode == "dependencies" and not any_missing:
        ledger.success("No missing dependencies found.")


# ===================== User Side Install Logic =====================
def install_dependencies(game_path, manifest_path, allowlist):
    content_path = os.path.join(game_path, "Content")
    if not os.path.isdir(content_path):
        ledger.error("No Content folder found.")
        return

    mod_folders = [f for f in os.listdir(content_path) if os.path.isdir(os.path.join(content_path, f))]
    installed_mods = {}
    for f in mod_folders:
        mod_toml_path = os.path.join(content_path, f, "mod.toml")
        if not os.path.exists(mod_toml_path):
            continue
        mod_name = read_mod_name(mod_toml_path, ledger)
        if mod_name:
            installed_mods[mod_name.lower()] = f

    for folder in mod_folders:
        ksamm_toml = os.path.join(content_path, folder, KSAMM_FILE)
        if not os.path.exists(ksamm_toml):
            continue

        try:
            with open(ksamm_toml, "rb") as f:
                data = tomllib.load(f)

            for key, auto_install in [("dependencies", True), ("optional_dependencies", False)]:
                dep_list = data.get(key, [])
                if not isinstance(dep_list, list):
                    continue

                for dep in dep_list:
                    if isinstance(dep, dict):
                        dep_name = dep.get("name", "").strip()
                        dep_link = dep.get("link", "").strip()
                        if not dep_name or dep_name.lower() in installed_mods:
                            continue

                        if not auto_install:
                            choice = input(f"Optional dependency '{dep_name}' is missing. Install? (y/n): ").lower()
                            if choice != "y":
                                continue

                        ledger.heading(f"Installing dependency '{dep_name}' for {folder}...")
                        if dep_link not in allowlist:
                            choice = input(f"Dependency '{dep_name}' URL '{dep_link}' is not in your allowlist. Add and install? (y/n): ").lower()
                            if choice != "y":
                                ledger.error(f"Skipping installation of '{dep_name}' due to allowlist.")
                                continue
                            allowlist.append(dep_link)
                            save_paths(None, None, None, None, allowlist)

                        installed_folder = install_mod_from_link(dep_link, content_path)
                        if installed_folder:
                            installed_mods[dep_name.lower()] = installed_folder
                            ledger.success(f"Installed '{dep_name}' into folder '{installed_folder}'")
                        else:
                            ledger.error(f"Failed to install dependency '{dep_name}' from {dep_link}")


        except Exception as e:
            ledger.error(f"Error reading {ksamm_toml}: {e}")

    rebuild_manifest(manifest_path, game_path)
    ledger.success("Dependency installation complete and manifest updated.")


# ===================== Install Logic =====================
def install_mod_from_link(download_url, extract_dir):
    try:
        ledger.info(f"Downloading mod from {download_url}...")

        req = Request(download_url, headers={"User-Agent": "KSAMM-Updater"})
        with urlopen(req, context=ssl_context) as resp:
            data = resp.read()

        try:
            z = zipfile.ZipFile(io.BytesIO(data))
        except zipfile.BadZipFile:
            ledger.error(f"Downloaded file from {download_url} is not a valid zip.")
            return None

        z.extractall(extract_dir)
        folder_name = z.namelist()[0].split("/")[0]
        return folder_name

    except Exception as e:
        ledger.error(f"Failed to install mod from {download_url}: {e}")
        return None



# ===================== Updates =====================
def check_for_updates():
    ledger.info("Checking for KSAMM updates...")
    try:
        req = Request(GITHUB_RELEASES_API)
        with urlopen(req, context=ssl_context) as r:
            data = json.load(r)

        latest = data.get("tag_name")
        if not latest:
            ledger.error("Could not determine latest release version from GitHub.")
            return None, None

        latest = latest.lstrip("v")

        if latest == KSAMM_VERSION:
            ledger.info(f"Already at latest version ({KSAMM_VERSION})")
            return latest, None

        ledger.info(f"New version available: {latest}")
        ledger.info(f"SpaceDock URL: {SPACEDOCK_DOWNLOAD}")

        return latest, SPACEDOCK_DOWNLOAD

    except Exception as e:
        ledger.error(f"Update check failed: {e}")
        return None, None

def startup_update_warn():
    try:
        req = Request(GITHUB_RELEASES_API)
        with urlopen(req, context=ssl_context) as r:
            data = json.load(r)
        latest = data.get("tag_name")
        if not latest:
            ledger.error("Unable to get latest update information.")
            return None, None
        if latest == KSAMM_VERSION:
            return latest, None
        ledger.heading(f"New KSAMM Version Available: {latest}")
    except Exception as e:
        ledger.error(f"{e}")


def install_update(download_url):
    ledger.info("Downloading update...")
    tmp_zip = os.path.join(tempfile.gettempdir(), "ksam_update.zip")
    try:
        with urlopen(Request(download_url), context=ssl_context) as r, open(tmp_zip,"wb") as f:
            f.write(r.read())
    except Exception as e:
        ledger.error(f"Failed to download update: {e}")
        return
    ledger.info("Download complete. Extracting update...")
    extract_dir = os.path.join(tempfile.gettempdir(), "ksam_update_extract")
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(tmp_zip,"r") as z:
        z.extractall(extract_dir)
    ledger.success("Update extracted.")
    install_dir = os.path.dirname(sys.executable if getattr(sys,"frozen",False) else __file__)
    updater_path = os.path.join(install_dir, "UpdateHelper.exe")
    if not os.path.exists(updater_path):
        ledger.error("UpdateHelper.exe not found.")
        return
    ledger.info("Starting updater...")
    subprocess.Popen([updater_path, extract_dir, install_dir], close_fds=True)
    time.sleep(0.2)
    sys.exit(0)

def check_starmap_update():
    ledger.info("Checking for StarMap updates...")

    # Load current version from config
    _, _, _, curr_starmap_version, allowlist = load_paths()

    if not curr_starmap_version:
        ledger.info("No current StarMap version found, assuming fresh install.")
        curr_starmap_version = "0.0.0"

    try:
        req = Request(STARMAP_DOWNLOAD)
        with urlopen(req, context=ssl_context) as r:
            data = json.load(r)

        latest_starmap = data.get("tag_name")
        if not latest_starmap:
            ledger.error("Could not determine latest release version from GitHub.")
            return None, None

        latest_starmap = latest_starmap.lstrip("v")

        if latest_starmap == curr_starmap_version:
            ledger.info(f"Already at latest version ({curr_starmap_version})")
            return latest_starmap, None

        ledger.info(f"New version available: {latest_starmap}")
        ledger.info(f"GitHub URL: {STARMAP_DOWNLOAD}")

        # Return GitHub URL for download
        return latest_starmap, STARMAP_DOWNLOAD

    except Exception as e:
        ledger.error(f"Update check failed: {e}")
        return None, None


def update_starmap(mod_loader_path):
    if not mod_loader_path:
        ledger.error("Mod loader path not set. Cannot update StarMap.")
        return

    ledger.info("Updating StarMap...")

    try:
        response = requests.get(STARMAP_DOWNLOAD)
        response.raise_for_status()
        latest_release = response.json()
        mod_loader_version = latest_release.get("tag_name")

        zip_asset = next((a for a in latest_release["assets"] if a["name"].endswith(".zip")), None)
        if not zip_asset:
            ledger.error("No .zip release found!")
            return

        zip_url = zip_asset["browser_download_url"]
        ledger.info(f"Downloading {zip_asset['name']}...")
        r = requests.get(zip_url)
        r.raise_for_status()

        z = zipfile.ZipFile(io.BytesIO(r.content))
        os.makedirs(mod_loader_path, exist_ok=True)
        z.extractall(mod_loader_path)

        ledger.info(f"StarMap updated to {mod_loader_version} at {mod_loader_path}")

        # Update StarMapConfig.json if it exists
        starmap_config_path = os.path.join(mod_loader_path, "StarMapConfig.json")
        if os.path.exists(starmap_config_path):
            with open(starmap_config_path, "r") as f:
                config_data = json.load(f)
            config_data["GameLocation"] = config_data.get("GameLocation", "")
            config_data["RepositoryLocation"] = config_data.get("RepositoryLocation", "")
            with open(starmap_config_path, "w") as f:
                json.dump(config_data, f, indent=4)
            ledger.info(f"StarMapConfig.json updated at {starmap_config_path}")

        return mod_loader_version

    except Exception as e:
        ledger.error(f"Error updating StarMap: {e}")


# ===================== Game Launch =====================
def launch_game(game_path, mod_loader_path=None):
    game_exe = os.path.join(game_path, "KSA.exe")
    mod_loader_exe = None
    if mod_loader_path:
        for exe_name in mod_loader_candidates:
            candidate = os.path.join(mod_loader_path, exe_name)
            if os.path.exists(candidate):
                mod_loader_exe = candidate
                break
    if mod_loader_exe:
        ledger.info(f"Launching game via Mod Loader: {mod_loader_exe}")
        subprocess.Popen([mod_loader_exe], cwd=mod_loader_path)
        return
    if os.path.exists(game_exe):
        ledger.info(f"Launching game directly: {game_exe}")
        subprocess.Popen([game_exe], cwd=game_path)
        return
    ledger.error("Could not find game executable or mod loader.")
    ledger.info(f"Tried:\n  Mod Loader: {mod_loader_exe or '[mod loader disabled]'}\n  Game EXE: {game_exe}")

# ===================== Main Loop =====================
def main():
    initialize()
    while True:
        ledger.header("KSAMM Main Menu")
        print("1. Set paths")
        print("2. Install mods")
        print("3. Manage installed mods")
        print("4. Check for updates")
        print("5. Launch game")
        print("6. Show metadata")
        print("q. Quit")
        choice = input("Choose an option: ")

        if choice == "1":
            ledger.heading("Path Setup")
            print("1. Enter paths manually")
            print("2. Auto-detect paths")
            sub_choice = input("Choose option: ")

            if sub_choice == "1":
                manifest = require_kitten_path(
                    "Manifest", "Enter path to manifest (or cancel):", ["manifest.toml"]
                )
                game_path = require_kitten_path(
                    "Game", "Enter game directory (or cancel):", ["KSA.exe"]
                )
                if not game_path:
                    ledger.error("Game path required.")
                    continue
                use_mod_loader = input("Use mod loader? (y/n): ").lower() == "y"
                mod_loader_path = None
                if use_mod_loader:
                    mod_loader_path = require_kitten_path(
                        "Mod Loader",
                        "Enter mod loader directory (or cancel):",
                        mod_loader_candidates
                    )

            elif sub_choice == "2":
                manifest, game_path, mod_loader_path, mod_loader_version, _ = find_paths()
                if not game_path or not manifest:
                    ledger.error("Auto-detection failed for required paths. Please enter manually.")
                    continue
                use_mod_loader = mod_loader_path is not None
                if use_mod_loader:
                    ledger.info("Mod loader auto-detected.")
                else:
                    ledger.info("Mod loader not found (optional).")
            else:
                ledger.error("Invalid choice.")
                continue

            save_paths(manifest, game_path, mod_loader_path, mod_loader_version, _)

        elif choice == "2":
            manifest, game_path, mod_loader_path, mod_loader_version, allowlist = load_paths()
            if not game_path:
                ledger.error("Game path not set.")
                continue
            install_mods(manifest, game_path)
            check_for_metadata(manifest, game_path, allowlist, mode = "dependencies")

        elif choice == "3":
            manifest, game_path, mod_loader_path, mod_loader_version, allowlist = load_paths()
            if not game_path:
                ledger.error("Game path not set.")
                continue
            manage_mods(manifest, game_path)

        elif choice == "4":
            manifest, game_path, mod_loader_path, mod_loader_version, allowlist = load_paths()

            if mod_loader_path:
                latest_starmap, url = check_starmap_update()

                if latest_starmap and latest_starmap != mod_loader_version:
                    if input(f"New StarMap version, {latest_starmap}, install now? (y/n)").lower() == "y":
                        mod_loader_version = update_starmap(mod_loader_path)
                        save_paths(manifest, game_path, mod_loader_path, mod_loader_version, allowlist)

            latest, url = check_for_updates()
            if latest and latest != KSAMM_VERSION:
                if input("Install now? (y/n): ").lower() == "y":
                    install_update(url)

        elif choice == "5":
            _, game_path, mod_loader_path, _, allowlist = load_paths()
            if not game_path:
                ledger.error("Game path not set.")
                continue
            launch_game(game_path, mod_loader_path)

        elif choice == "6":
            manifest, game_path, mod_loader_path, mod_loader_version, allowlist = load_paths()
            check_for_metadata(manifest, game_path, "metadata")

        elif choice.lower() == "q":
            break

        else:
            ledger.error("Invalid choice.")


if __name__ == "__main__":
    main()
