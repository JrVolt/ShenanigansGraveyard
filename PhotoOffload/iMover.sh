#!/bin/bash

# Define the source folder (change as needed)
SOURCE_FOLDER="/mnt/168025a7-49f2-47da-946a-713ecb5bee89/_WORK_/MartaPapi/iTest"

# Move to the source folder
cd "$SOURCE_FOLDER" || exit

# Loop through all image files in the folder
for file in *.{jpg,JPG,jpeg,JPEG,png,PNG,heic,HEIC,mov,MOV,mp4,MP4}; do
    # Skip if no matching files
    [ -e "$file" ] || continue

    # Extract the year from EXIF metadata
    year=$(exiftool -d "%Y" -DateTimeOriginal -S -s "$file" 2>/dev/null)

    # If the file has no EXIF DateTimeOriginal, try another tag
    if [ -z "$year" ]; then
        year=$(exiftool -d "%Y" -CreateDate -S -s "$file" 2>/dev/null)
    fi

    # If still no year, default to "Unknown"
    if [ -z "$year" ]; then
        year="Unknown"
    fi

    # Create the directory if it doesn't exist
    mkdir -p "$year"

    # Move the file to the corresponding year folder
    mv "$file" "$year/"

    echo "Moved: $file → $year/"
done

echo "Sorting complete!"
