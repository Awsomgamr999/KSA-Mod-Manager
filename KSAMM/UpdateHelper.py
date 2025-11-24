import os
import sys
import time
import shutil
import subprocess

def is_process_running(name):
    try:
        out = subprocess.check_output('tasklist', shell=True).decode()
        return name.lower() in out.lower()
    except Exception:
        return False

def wait_for_process_exit(name, check_interval=0.2, timeout=30):
    start_time = time.time()
    while is_process_running(name):
        if time.time() - start_time > timeout:
            print(f"Warning: {name} did not exit after {timeout}s, continuing anyway.")
            break
        time.sleep(check_interval)

def delete_existing(dest):
    if os.path.exists(dest):
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        else:
            os.remove(dest)

def copy_update(src_folder, dest_folder):
    for root, dirs, files in os.walk(src_folder):
        rel_path = os.path.relpath(root, src_folder)
        target_dir = os.path.join(dest_folder, rel_path)
        os.makedirs(target_dir, exist_ok=True)
        for file in files:
            if file.lower() == "updatehelper.exe":
                continue  # skip overwriting the updater itself
            src_file = os.path.join(root, file)
            dest_file = os.path.join(target_dir, file)
            delete_existing(dest_file)
            shutil.copy2(src_file, dest_file)


def find_update_root(temp_folder):
    for root, dirs, files in os.walk(temp_folder):
        for f in files:
            if f.lower() == "ksamodmanager.exe":
                return root
    return temp_folder

def remove_artifact_folders(install_folder):
    """
    Remove any artifact folders created by zip extraction:
    - KSAModManager
    - _internal
    """
    for folder_name in ["KSAModManager", "_internal"]:
        folder_path = os.path.join(install_folder, folder_name)
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            try:
                shutil.rmtree(folder_path)
                print(f"Removed artifact folder: {folder_name}")
            except Exception as e:
                print(f"Warning: Could not remove {folder_name}: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: UpdateHelper.exe <temp_folder> <install_folder>")
        sys.exit(1)

    temp_folder = sys.argv[1]
    install_folder = sys.argv[2]
    ksam_exe_name = "KSAModManager.exe"
    ksam_exe_path = os.path.join(install_folder, ksam_exe_name)

    print("Waiting for KSAMM to close...")
    wait_for_process_exit(ksam_exe_name)

    print("Finding update root folder...")
    update_root = find_update_root(temp_folder)
    print(f"Update root detected: {update_root}")

    print("Applying update...")
    copy_update(update_root, install_folder)
    print("Update applied successfully.")

    print("Removing artifact folders if any...")
    remove_artifact_folders(install_folder)

    print("Cleaning up temporary files...")
    try:
        shutil.rmtree(temp_folder)
        print(f"Temporary folder {temp_folder} removed.")
    except Exception as e:
        print(f"Warning: Could not delete temp folder: {e}")

    if os.path.exists(ksam_exe_path):
        print(f"Starting KSAMM from: {ksam_exe_path}")
        try:
            subprocess.Popen([ksam_exe_path], shell=False)
            print("Update complete. KSAMM launched.")
        except Exception as e:
            print(f"ERROR: Failed to launch KSAMM: {e}")
    else:
        print(f"ERROR: {ksam_exe_name} not found in install folder!")

    sys.exit(0)

if __name__ == "__main__":
    main()
