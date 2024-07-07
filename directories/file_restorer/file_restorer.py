import os
from pathlib import Path
import logging

def setup_logger(log_file):
    logging.basicConfig(filename=log_file, level=logging.ERROR,
                        format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

def log_failed_file(file_path, error):
    logging.error(f"Failed to restore: {file_path}\nError: {error}")

def restore_file_structure(consolidated_file, log_file):
    setup_logger(log_file)
    root_dir = None
    current_file = None
    content = []
    output_dir = Path("rebuild")
    
    with open(consolidated_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            if line.startswith("# Root Directory: "):
                root_dir = line.split(": ", 1)[1].strip()
            elif line.startswith("# File: "):
                if current_file:
                    write_file(current_file, content, log_file)
                relative_path = line.split(": ", 1)[1].strip()
                current_file = output_dir / relative_path
                content = []
            elif line.startswith("# Full path: "):
                pass  # We don't need this for restoration
            elif line.startswith("# Hidden: "):
                pass  # We don't handle setting hidden attribute in this script
            elif line.startswith("# --- Start of file content ---"):
                content = []
            elif line.startswith("# --- End of file content ---"):
                write_file(current_file, content, log_file)
                current_file = None
            elif not line.startswith("#"):
                content.append(line)

    if current_file:
        write_file(current_file, content, log_file)

    print(f"File structure restored in {output_dir}")
    print(f"Check {log_file} for any errors encountered during restoration")

def write_file(path, content, log_file):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as outfile:
            outfile.writelines(content)
    except Exception as e:
        log_failed_file(path, str(e))

if __name__ == "__main__":
    consolidated_file = input("Enter the path to the consolidated file: ").strip()
    root_directory = Path(consolidated_file).parent
    log_file = root_directory / "restoration_log.txt"
    
    restore_file_structure(consolidated_file, log_file)
