#!/usr/bin/env python3
import os

# Folder to fix (change as needed)
root_folder = "."

# Number of spaces per tab
TAB_SIZE = 4

def normalize_file(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    changed = False
    for line in lines:
        # Determine leading whitespace
        leading = len(line) - len(line.lstrip("\t "))
        indent = line[:leading]
        content = line[leading:]

        # Replace tabs with spaces and normalize all indentation
        normalized_indent = indent.replace("\t", " " * TAB_SIZE)
        if normalized_indent != indent:
            changed = True

        new_lines.append(normalized_indent + content)

    if changed:
        # Backup original
        os.rename(file_path, file_path + ".bak")
        # Write normalized file
        with open(file_path, "w") as f:
            f.writelines(new_lines)
        print(f"Normalized: {file_path} (backup: {file_path}.bak)")

def normalize_folder(folder):
    for dirpath, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            if filename.endswith(".py"):
                normalize_file(os.path.join(dirpath, filename))

if __name__ == "__main__":
    normalize_folder(root_folder)
    print("Done normalizing Python files to 4-space indentation.")