import os
from pathlib import Path
import logging
import stat

def setup_logger(log_file):
    logging.basicConfig(filename=log_file, level=logging.ERROR,
                        format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

def log_failed_file(file_path, error):
    logging.error(f"Failed to consolidate: {file_path}\nError: {error}")

def is_hidden(filepath):
    name = os.path.basename(os.path.abspath(filepath))
    return name.startswith('.') or bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)

def consolidate_files(root_dir, output_file, log_file):
    setup_logger(log_file)
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(f"# Root Directory: {root_dir}\n\n")
        for root, dirs, files in os.walk(root_dir):
            # Include all files, including hidden ones
            all_files = [f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]
            
            rel_path = os.path.relpath(root, root_dir)
            if rel_path != '.':
                outfile.write(f"\n# Directory: {rel_path}\n")
            
            for file in all_files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(root_dir)
                outfile.write(f"\n# File: {relative_path}\n")
                outfile.write(f"# Full path: {file_path}\n")
                outfile.write(f"# Hidden: {'Yes' if is_hidden(file_path) else 'No'}\n")
                outfile.write("# --- Start of file content ---\n")
                try:
                    # Try to read the file as text
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except UnicodeDecodeError:
                    outfile.write(f"# This file is not a text file and its content cannot be displayed here.\n")
                    log_failed_file(file_path, "Not a text file")
                except Exception as e:
                    outfile.write(f"# Error reading file: {e}\n")
                    log_failed_file(file_path, str(e))
                outfile.write("\n# --- End of file content ---\n")

if __name__ == "__main__":
    root_directory = input("Enter the root directory path: ")
    output_file = input("Enter the output file name (including path if desired): ")
    log_file = input("Enter the log file name (including path if desired): ")
    
    consolidate_files(root_directory, output_file, log_file)
    print(f"All files consolidated into {output_file} with directory structure comments")
    print(f"Check {log_file} for any errors encountered during consolidation")