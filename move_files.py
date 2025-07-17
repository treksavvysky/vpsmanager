import os
import time
import shutil
import logging

def move_files_with_delay(source_dir, dest_dir, delay_seconds):
    """
    Moves all files from source_dir to dest_dir while preserving directory structure.
    """
    logging.basicConfig(filename='/app/file_move.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    print(f"Starting file transfer from {source_dir} to {dest_dir}...")

    try:
        for root, _, files in os.walk(source_dir):
            for filename in files:
                source_path = os.path.join(root, filename)

                # Get relative path of the file inside source_dir
                relative_path = os.path.relpath(source_path, source_dir)
                dest_path = os.path.join(dest_dir, relative_path)

                try:
                    # Create necessary directories in the destination
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                    # Move file while keeping structure
                    shutil.move(source_path, dest_path)
                    logging.info(f"Moved: {source_path} -> {dest_path}")
                    print(f"Moved: {source_path} -> {dest_path}")
                    
                    time.sleep(delay_seconds)  # Delay between moves
                except Exception as e:
                    logging.error(f"Error moving {source_path}: {e}")
                    print(f"Error moving {source_path}: {e}")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")

    print(f"Finished file transfer from {source_dir} to {dest_dir}.\n")

# Move OneDrive files to HiDrive (keeping structure)
move_files_with_delay("/app/onedrive", "/app/hidrive/onedrive", 5)

# Move Google Drive files to HiDrive (keeping structure)
move_files_with_delay("/app/gdrive", "/app/hidrive/googledrive", 5)