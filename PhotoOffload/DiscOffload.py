import os
import subprocess
import time
import platform

# Detect the system
SYSTEM = platform.system()
MOUNT_POINT = "/mnt/dvd" if SYSTEM == "Linux" else "/Volumes/DVD"

def get_desktop_path():
    return os.path.join(os.path.expanduser("~"), "Desktop")

def set_output_directory():
    print("\nWhere do you want to save the DVD dumps?")
    print(f"1) Use default (Desktop: {get_desktop_path()})")
    print("2) Set a custom directory")
    choice = input("Select an option (1/2): ").strip()

    if choice == "2":
        custom_dir = input("Enter the full path of your directory: ").strip()
        if os.path.isdir(custom_dir):
            return custom_dir
        print("Invalid directory! Using default Desktop instead.")

    return get_desktop_path()

def get_disc_info():
    device = "/dev/sr0" if SYSTEM == "Linux" else "/dev/disk2"  # Adjust for Mac
    if not os.path.exists(device):
        print("[!] No optical drive detected.")
        return None, None, None

    # Get filesystem label and type
    blkid_output = subprocess.run(["blkid", device], capture_output=True, text=True).stdout if SYSTEM == "Linux" else ""
    diskutil_output = subprocess.run(["diskutil", "info", device], capture_output=True, text=True).stdout if SYSTEM == "Darwin" else ""

    label, fs_type = None, None
    if SYSTEM == "Linux":
        if "LABEL=" in blkid_output:
            label = blkid_output.split('LABEL="')[1].split('"')[0]
        if "TYPE=" in blkid_output:
            fs_type = blkid_output.split('TYPE="')[1].split('"')[0]
    elif SYSTEM == "Darwin":
        for line in diskutil_output.split("\n"):
            if "Volume Name:" in line:
                label = line.split(":")[1].strip()
            if "File System Personality:" in line:
                fs_type = line.split(":")[1].strip()

    # Determine disc type
    disc_type = "Unknown"
    lsblk_output = subprocess.run(["lsblk", "-o", "NAME,SIZE", "-r", "/dev/sr0"], capture_output=True, text=True).stdout if SYSTEM == "Linux" else ""
    if "4.7G" in lsblk_output or "DVD" in blkid_output or "DVD" in diskutil_output:
        disc_type = "DVD"
    elif "8.5G" in lsblk_output:
        disc_type = "DVD-DL"
    elif "25G" in lsblk_output or "Blu-ray" in diskutil_output:
        disc_type = "Blu-ray"
    elif "700M" in lsblk_output:
        disc_type = "CD"

    # Get writing date
    date = time.strftime("%Y-%m-%d")  # Default to today
    if fs_type == "udf" and SYSTEM == "Linux":
        udf_output = subprocess.run(["udfinfo", device], capture_output=True, text=True).stdout
        for line in udf_output.splitlines():
            if "Recording time:" in line:
                date = line.split(": ")[1].strip().replace(" ", "_")
                break

    return disc_type, label, date

def copy_disc(destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    print(f"[*] Copying files to {destination_folder}...")
    
    if SYSTEM == "Linux":
        subprocess.run(["mount", "/dev/sr0", MOUNT_POINT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif SYSTEM == "Darwin":
        subprocess.run(["diskutil", "mount", "/dev/disk2"])

    subprocess.run(["rsync", "-av", f"{MOUNT_POINT}/", destination_folder])
    
    if SYSTEM == "Linux":
        subprocess.run(["umount", MOUNT_POINT])
    elif SYSTEM == "Darwin":
        subprocess.run(["diskutil", "unmount", "/dev/disk2"])
    
    print("[✔] Copy completed.")

def eject_disc():
    print("[*] Ejecting disc...")
    if SYSTEM == "Linux":
        subprocess.run(["eject", "/dev/sr0"])
    elif SYSTEM == "Darwin":
        subprocess.run(["diskutil", "eject", "/dev/disk2"])
    print("[✔] Disc ejected.")

def add_notes(destination_folder):
    add_note = input("Do you want to add a note for this disc? (y/n): ").strip().lower()
    if add_note == "y":
        note_file = os.path.join(destination_folder, "disc_notes.txt")
        print(f"[*] Opening {note_file} for writing...")
        with open(note_file, "w") as f:
            print("Write your note below. Type 'EOF' on a new line to save.")
            while True:
                line = input("> ")
                if line.strip().upper() == "EOF":
                    break
                f.write(line + "\n")
        print("[✔] Note saved.")

def main():
    print("\n=== DVD/CD Offloading Script ===")
    
    # Set the output directory once at the start
    output_dir = set_output_directory()
    print(f"\n[✔] All discs will be saved in: {output_dir}")

    while True:
        input("\nInsert a disc and press Enter... ")

        disc_type, label, date = get_disc_info()
        if disc_type is None:
            print("[!] No disc detected. Please check and try again.")
            continue

        label = label if label else "NoLabel"
        folder_name = f"{date}-{disc_type}-{label}".replace(" ", "_")
        destination_folder = os.path.join(output_dir, folder_name)

        print(f"\nDetected: {disc_type} | Label: {label} | Date: {date}")
        confirm = input(f"[?] Copy contents to {destination_folder}? (y/n): ").strip().lower()
        if confirm == 'y':
            copy_disc(destination_folder)
            add_notes(destination_folder)
            eject_disc()

        another = input("[?] Do you want to dump another disc? (y/n): ").strip().lower()
        if another != 'y':
            break

if __name__ == "__main__":
    main()
