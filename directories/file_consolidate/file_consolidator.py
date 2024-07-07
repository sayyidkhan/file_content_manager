import os
from pathlib import Path
import logging
from datetime import datetime

def setup_logger(log_file):
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(filename=log_file, level=logging.ERROR,
                        format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

def log_failed_file(file_path, error):
    logging.error(f"Failed to consolidate: {file_path}\nError: {error}")

def is_hidden(filepath):
    if os.name == 'nt':  # Windows
        import ctypes
        FILE_ATTRIBUTE_HIDDEN = 0x02
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(filepath))
        return attrs & FILE_ATTRIBUTE_HIDDEN
    else:  # Unix-based systems (macOS, Linux)
        return os.path.basename(filepath).startswith('.')

def consolidate_files(root_dir, output_file):
    # Ensure output_file is a file, not a directory
    if os.path.isdir(output_file):
        output_file = os.path.join(output_file, "consolidated_output.txt")
    
    output_dir = os.path.dirname(output_file)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(output_dir, f"consolidation_log_{timestamp}.txt")
    
    setup_logger(log_file)
    
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(f"# Root Directory: {root_dir}\n\n")
        for root, dirs, files in os.walk(root_dir):
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
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except UnicodeDecodeError:
                    outfile.write(f"# This file is not a text file and its content cannot be displayed here.\n")
                    log_failed_file(file_path, "Not a text file")
                except Exception as e:
                    outfile.write(f"# Error reading file: {e}\n")
                    log_failed_file(file_path, str(e))
                outfile.write("\n# --- End of file content ---\n")
    
    return log_file

def print_instructions():
    print("\nFile Content Manager - Consolidator")
    print("====================================")
    print("This script will consolidate the contents of a directory into a single file.")
    print("\nInstructions:")
    print("1. For the root directory path:")
    print("   - Enter the full path of the directory you want to consolidate")
    print("   - For the current directory, you can use '.' or './'")
    print("   Example: /Users/username/Documents/my_project or ./my_project")
    print("\n2. For the output file name:")
    print("   - Enter the full path and filename where you want to save the consolidated content")
    print("   - If you only provide a directory, a default filename will be used")
    print("   Example: /Users/username/Desktop/consolidated_output.txt or ./output/result.txt")
    print("\nThe script will automatically create a log file in the same directory as the output file.")
    print("====================================\n")

if __name__ == "__main__":
    print_instructions()
    
    while True:
        root_directory = input("Enter the root directory path: ").strip()
        if os.path.isdir(root_directory):
            break
        print("Error: The specified path is not a valid directory. Please try again.")

    while True:
        output_file = input("Enter the output file name (including path if desired): ").strip()
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                print(f"Error creating directory: {e}")
                continue
        break

    try:
        log_file = consolidate_files(root_directory, output_file)
        print(f"\nAll files consolidated into {output_file} with directory structure comments")
        print(f"Check {log_file} for any errors encountered during consolidation")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check your inputs and try again.")
