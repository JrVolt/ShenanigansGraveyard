import os
import shutil
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Set

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PhotoOrganizer:
    def __init__(self, source_folder: str, dry_run: bool = False):
        self.source_path = Path(source_folder).resolve()
        self.dry_run = dry_run
        self.processed_files: Set[str] = set()
        
        # Supported file extensions (all lowercase)
        self.image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".heic", ".mov", ".mp4"}
        self.sidecar_extensions = {".aae", ".xml", ".xmp"}
        
        # Ensure source exists
        if not self.source_path.is_dir():
            raise ValueError("❌ Error: Source folder does not exist!")

    def is_supported_extension(self, file_path: Path) -> bool:
        ext = file_path.suffix.lower()
        return ext in self.image_extensions or ext in self.sidecar_extensions

    def get_oldest_year(self, file_path: Path) -> str:
        try:
            result = subprocess.run(
                ["exiftool", "-d", "%Y:%m:%d %H:%M:%S", "-DateTimeOriginal", "-CreateDate", "-FileModifyDate", "-S", "-s", 
                 str(file_path)],
                capture_output=True, text=True, check=True
            )
            
            date_list = []
            for line in result.stdout.splitlines():
                try:
                    date_obj = datetime.strptime(line.strip(), "%Y:%m:%d %H:%M:%S")
                    date_list.append(date_obj)
                except ValueError:
                    continue
                    
            return str(min(date_list).year) if date_list else "Unknown"
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running exiftool on {file_path}: {e}")
            return "Unknown"
        except Exception as e:
            logging.error(f"Error processing dates for {file_path}: {e}")
            return "Unknown"

    def find_live_photo_components(self, base_name: str) -> Dict[str, Optional[Path]]:
        components = {
            'still': None,    # HEIC file
            'video': None,    # MOV file
            'edit': None      # AAE file
        }
        
        # Search in source and all year folders
        search_paths = [self.source_path] + [
            d for d in self.source_path.iterdir() if d.is_dir()
        ]
        
        for folder in search_paths:
            for file in folder.iterdir():
                if not file.is_file():
                    continue
                    
                # Check both regular name and 'O' suffix (case-insensitive)
                if file.stem.lower() == base_name.lower() or file.stem.lower() == f"{base_name}O".lower():
                    ext = file.suffix.lower()
                    if ext == '.heic':
                        components['still'] = file
                    elif ext == '.mov':
                        components['video'] = file
                    elif ext == '.aae':
                        components['edit'] = file
        
        return components

    def safe_move(self, source: Path, dest_folder: Path) -> bool:
        try:
            if not source.exists():
                logging.warning(f"Source file not found: {source}")
                return False
            
            if self.dry_run:
                logging.info(f"Would move: {source} → {dest_folder}/")
                return True
            
            dest_folder.mkdir(parents=True, exist_ok=True)
            dest_path = dest_folder / source.name
            
            if dest_path.exists():
                logging.warning(f"File already exists at destination: {dest_path}")
                return False
                
            shutil.move(str(source), str(dest_path))
            logging.info(f"📂 Moved: {source.name} → {dest_folder}/")
            return True
            
        except PermissionError:
            logging.error(f"Permission denied moving {source}")
            return False
        except Exception as e:
            logging.error(f"Error moving {source}: {e}")
            return False

    def move_live_photo(self, components: Dict[str, Optional[Path]]) -> None:
        year = "Unknown"
        if components['still']:
            year = self.get_oldest_year(components['still'])
        elif components['video']:
            year = self.get_oldest_year(components['video'])
        
        dest_folder = self.source_path / year
        
        for file_type, file_path in components.items():
            if file_path and file_path.exists():
                if self.safe_move(file_path, dest_folder):
                    self.processed_files.add(file_path.stem.lower())  # Store lowercase stem

    def process_remaining_file(self, file: Path) -> None:
        if not self.is_supported_extension(file):
            return
            
        ext = file.suffix.lower()
        if ext in self.image_extensions:
            year = self.get_oldest_year(file)
            dest_folder = self.source_path / year
            self.safe_move(file, dest_folder)
        
        elif ext in self.sidecar_extensions:
            dest_folder = self.source_path / "Unknown"
            self.safe_move(file, dest_folder)
            logging.warning(f"⚠️ Orphaned sidecar file: {file.name}")

    def organize(self) -> None:
        logging.info("🎥 Processing Live Photos...")
        
        for file in self.source_path.iterdir():
            if not file.is_file() or file.stem.lower() in self.processed_files:
                continue
                
            components = self.find_live_photo_components(file.stem)
            component_count = sum(1 for c in components.values() if c is not None)
            
            if component_count >= 2:
                logging.info(f"\n📸 Found Live Photo components for {file.stem}:")
                for file_type, file_path in components.items():
                    if file_path:
                        logging.info(f"  - {file_type}: {file_path.name}")
                self.move_live_photo(components)
        
        logging.info("\n📷 Processing remaining files...")
        for file in self.source_path.iterdir():
            if file.is_file() and file.stem.lower() not in self.processed_files:
                self.process_remaining_file(file)
        
        logging.info("\n✅ Sorting complete!")

if __name__ == "__main__":
    print("📸 Photo Sorter")
    print("------------------------------------------")
    
    # Source folder
    while True:
        source_folder = input("\nEnter the source folder path: ").strip().strip('"').strip("'")
        if os.path.isdir(source_folder):
            break
        print("❌ Error: Folder not found. Enter a valid path.")
    
    # Dry run
    while True:
        dry_run_response = input("\nDo you want to do a dry run first? (y/n): ").lower()
        if dry_run_response in ['y', 'n']:
            break
        print("Enter 'y/n' ")
    
    dry_run = dry_run_response == 'y'
    
    if dry_run:
        print("\n🔍 Dry run mode - No files will be moved")
    
    try:
        organizer = PhotoOrganizer(source_folder, dry_run)
        
        # Last confirmation 
        if not dry_run:
            proceed = input("\n⚠️ Move files in the folder? (Type 'yEs'): ")
            if proceed != 'yEs':
                print("\n❌ Operation cancelled")
                exit(0)
        
        print("\n🚀 Starting organization...")
        organizer.organize()
        
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        exit(1)