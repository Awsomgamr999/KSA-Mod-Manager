import os
import sys
import time
import shutil
import subprocess

def is_process_running(name):
    try:
        out = subprocess.check_output('tasklist', shell=True).decode()
        return name.lower() in out.lower()
    except:
        return False

def find_update_root(temp_folder):
    """
    Find the folder inside temp_folder that contains the real .exe.
    Returns the path to that folder.
    """
    for entry in os.listdir(temp_folder):
        entry_path = os.path.join(temp_folder, entry)
        if os.path.isdir(entry_path):
            # Search for .exe inside
            for root, dirs, files in os.walk(entry_path):
                for f in files:
                    if f.lower().endswith(".exe"):
                        return entry_path
    return temp_folder  # fallback (if update is flat / no nested folder)

def delete_existing_install(dest):
    """Delete existing file/folder before copying."""
    if os.path.exists(dest):
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        else:
            os.remove(dest)

def main():
    if len(sys.argv) < 3:
        print("Usage: UpdateHelper.exe <temp_folder> <install_folder>")
        sys.exit(1)

    temp_folder = sys.argv[1]
    install_folder = sys.argv[2]
    ksam_exe = os.path.join(install_folder, "KSAModManager.exe")

    print("Waiting for KSAMM to close...")

    # Wait for KSAMM.exe to stop running
    while is_process_running("KSAModManager.exe"):
        time.sleep(0.5)

    print("Finding update root folder...")
    update_root = find_update_root(temp_folder)
    print(f"Update root detected: {update_root}")

    print("Applying update...")

    # Copy files from update_root into install_folder
    for root, dirs, files in os.walk(update_root):
        rel = os.path.relpath(root, update_root)
        dest_dir = os.path.join(install_folder, rel)

        os.makedirs(dest_dir, exist_ok=True)

        for file in files:
            src = os.path.join(root, file)
            dest = os.path.join(dest_dir, file)

            delete_existing_install(dest)
            shutil.copy2(src, dest)

    print("Cleaning up temporary files...")
    try:
        shutil.rmtree(temp_folder)
    except Exception as e:
        print(f"Warning: Could not delete temp folder: {e}")

    print("Starting new KSAMM...")
    subprocess.Popen([ksam_exe], shell=False)

    print("Update complete.")
    sys.exit(0)

if __name__ == "__main__":
    main()
