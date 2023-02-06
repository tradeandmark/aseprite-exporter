#!/usr/bin/python3

import hashlib
import os
import sys
import subprocess

print("Sprite exporter!")

## Terminal colour stuff

colours = {
    "bold": "\x1b[1m",
    "red": "\x1b[31m",
    "yellow": "\x1b[33m",
    "green": "\x1b[32m",
    "reset": "\x1b[0m"
}

def c(string, name):
    return colours[name] + string + colours['reset']

if os.name == "nt":
    # Enables terminal colours in cmd.exe. Only supported in Windows builds >= 14393
    # https://stackoverflow.com/a/36760881
    import ctypes
    kernel32 = ctypes.windll.kernel32
    err = kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 0b111) # -11 = stdout
    if err == 0: # 0 indicates an error
        for k in colours:
            colours[k] = ''


## Stage 1: Find existing .ase and .ase.png files, and read hash file

print(c("Reading asset files and hash file", "bold"))

ase_files, png_files = [], []

# Hashes of each file on disk, for comparison with last exported hashes
newhashes = {}
# Find .ase files in assets/sprites/ase
for (dirname, _, filenames) in os.walk("assets/sprites/ase"):
    for name in sorted(filenames):
        if name.endswith(".ase"):
            fullpath = dirname + "/" + name
            ase_files.append(os.path.relpath(fullpath, "assets/sprites/ase"))
            # Hash each file
            with open(fullpath, "rb") as f:
                    newhashes[
                        os.path.relpath(fullpath, "assets/sprites/ase")
                    ] = hashlib.sha256(f.read()).hexdigest()
# Find .ase.png files in assets/sprites/png
for (dirname, _, filenames) in os.walk("assets/sprites/png"):
    for name in filenames:
        if name.endswith(".ase.png"):
            png_files.append(os.path.relpath(dirname + "/" + name[:-4], "assets/sprites/png"))

# Hashes stored from the last time sprites were exported in assets/sprites/.hashes
oldhashes = {}
hashfile_count = 1
try:
    with open("assets/sprites/.hashes", "r") as f:
        for line in f.read().split('\n'):
            if not line.startswith("# ") and line.strip() != "":
                [name, hash] = line.rsplit(' ', 1)
                oldhashes[name] = hash
except FileNotFoundError:
    hashfile_count = 0
except Exception as e:
    raise e

print(f"Found (and hashed) {len(ase_files)} .ase files, {len(png_files)} .png files and {hashfile_count} hash files containing {len(oldhashes.keys())} hashes")
# print(oldhashes, newhashes) # YAYAYAYA


## Stage 2: Work out which things need to be exported, (re)exported or deleted

print(c("\nIdentifying new, changed, deleted and unchanged files", "bold"))

to_export, to_delete = [], []
new_count, changed_count, deleted_count, unchanged_count = 0, 0, 0, 0

# Iterate through ase files, check for changes
for ase in ase_files:

    # New .ase file (ase exists but no png):
    # - Add png to export list, regardless of current hash
    if ase not in png_files:
        print(c(f"  + {ase}", "green"))
        new_count += 1
        to_export.append(ase)

    else:
        # .ase file is not new
        # - Check if the hash is changed
        if ase not in oldhashes or newhashes[ase] != oldhashes[ase]:
            # Hash is changed
            # - Add ase to export
            print(c(f"  ~ {ase}", "yellow"))
            changed_count += 1
            to_export.append(ase)
        else:
            # Hash is unchanged
            # - Do nothing
            unchanged_count += 1

for png in png_files:
    # Deleted ase file (png exists but no ase):
    # - Add png to delete list
    if png not in ase_files:
        print(c(f"  - {png}", "red"))
        deleted_count += 1
        to_delete.append(png + ".png")

print(f"{new_count} new, {changed_count} changed, {deleted_count} deleted and {unchanged_count} unchanged")

if new_count == 0 and changed_count == 0 and deleted_count == 0:
    print("Nothing to do!")
    exit()

if "--preview" in sys.argv:
    print("Preview mode enabled, exiting before making changes")
    exit()

## Stage 3: export all the things

print(c("\nWriting to all files!", "bold"))

for file in to_delete:
    print(f"  Deleting {file}")
    os.remove("assets/sprites/png/" + file)
    try:
        os.remove(f"assets/sprites/png/{file}.import")
    except Exception:
        pass

for file in to_export:
    print(f"  Exporting {file} to assets/sprites/png/{file}.png... ", end='')
    
    command = ["aseprite", "-b", f"assets/sprites/ase/{file}", "--sheet", f"assets/sprites/png/{file}.png", "--sheet-type", "horizontal"]
    pipes = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = pipes.communicate()

    if len(std_err) or pipes.returncode != 0:
        print(c(f"Error ({pipes.returncode}):\n{std_err.decode(sys.getfilesystemencoding()).strip()}", "red"))
    else:
        print("Done")


## Stage 4: update hash file

print(c("\nUpdating hash list", "bold"))

with open("assets/sprites/.hashes", "w", encoding="utf-8", newline="\n") as f:
    f.write("# Generated by spriteexporter.py\n")
    for k in newhashes:
        f.write(f"{k} {newhashes[k]}\n")

print("Done!")