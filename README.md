# Aseprite Exporter

A utility script written in Python that that automatically scans for aseprite files and synchronises png exports.

<!-- Screenshot -->

## Usage

```
$ ./aseprite-exporter.py --help
usage: aseprite-exporter.py [-h] [--path PATH] [--ase-dir ASE_DIR] [--png-dir PNG_DIR] [--hashfile HASHFILE] [--live-update] [--preview] [--nopretty]

Automatically exports aseprite files

optional arguments:
  -h, --help           show this help message and exit
  --path PATH          base path of directories that contain asset files
  --ase-dir ASE_DIR    directory containing .ase source files, relative to --path
  --png-dir PNG_DIR    directory containing .png export files, relative to --path
  --hashfile HASHFILE  path to the file dedicated to storing the file hashes
  --live-update        enable a mode where the script will continuously wait for file changes
  --preview            preview changes without writing to any files
  --nopretty           don't use fancy formatting
```
