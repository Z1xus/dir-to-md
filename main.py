import os
import argparse
from pathlib import Path

def process_file(path: Path, base_path: Path, out_file):
    rel_path = os.path.relpath(path, base_path)
    rel_path = rel_path.replace('\\', '/')
    ext = path.suffix.replace('.', '')

    out_file.write(f"{rel_path}:\n")
    out_file.write("```" + ext + "\n")

    try:
        with path.open(encoding='utf-8') as f:
            out_file.write(f.read())
    except UnicodeDecodeError:
        try:
            with path.open(mode='rb') as f:
                out_file.write(f.read().decode('utf-8', errors='replace'))
        except Exception as e:
            out_file.write(f"This file could not be decoded. Error: {str(e)}\n")

    out_file.write("\n```\n\n")

def process_folder(base_path: Path, folder_path: Path, out_file, ignore_patterns=set(), ignored_extensions=set()):
    for item in folder_path.iterdir():
        if item.name in {".git", ".gitignore", ".eslintignore", ".prettierignore"} or item.suffix in ignored_extensions or any(item.match(pattern) for pattern in ignore_patterns):
            continue
        if item.is_file():
            process_file(item, base_path, out_file)
        elif item.is_dir():
            process_folder(base_path, item, out_file, ignore_patterns, ignored_extensions)

def get_ignore_patterns(folder_path: Path, ignore_filenames):
    patterns = []
    for ignore_filename in ignore_filenames:
        ignore_path = folder_path / ignore_filename
        if ignore_path.is_file():
            with ignore_path.open(encoding='utf-8') as f:
                patterns += [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]
    return patterns

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="Input file or folder", required=True)
    parser.add_argument("-o", "--output", help="Output filename", required=True)

    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output)

    # add any extensions you want to ignore here
    ignored_extensions = {".png", ".jpg", ".bmp", ".svg", ".pdf", ".tif", ".tiff", ".gif", ".mp4", ".webm", ".avi", ".mp3", ".aac", ".wav", ".ogg", ".7z", ".zip", ".rar", ".cube", ".exe"}

    ignore_filenames = [".gitignore", ".eslintignore", ".prettierignore"]
    ignore_patterns = get_ignore_patterns(input_path, ignore_filenames)

    with output_path.open('w', encoding='utf-8') as out_file:
        if input_path.is_file() and input_path.suffix not in ignored_extensions:
            process_file(input_path, input_path.parent, out_file)
        elif input_path.is_dir():
            process_folder(input_path, input_path, out_file, ignore_patterns, ignored_extensions)

if __name__ == "__main__":
    main()
