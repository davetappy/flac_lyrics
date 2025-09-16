# FLAC Lyrics Fetcher

A Python script that scans a directory (and all subdirectories) for `.flac` music files, queries the [lrclib.net](https://lrclib.net) API for **synced lyrics**, and:

1. Creates a `.lrc` file in the same folder as the music file.
2. Embeds the lyrics into the FLAC file’s `LYRICS` tag.

The script supports safe modes (skip, prompt, dry-run) as well as force-overwrite, and can output logs for auditing.

---

## Features
- ✅ Recursively scans for `.flac` files  
- ✅ Fetches synced lyrics (falls back to plain lyrics if needed)  
- ✅ Creates `.lrc` files with the same base name as the music file  
- ✅ Embeds lyrics directly into the FLAC file’s metadata  
- ✅ Skips files that already have lyrics (unless `--force` is used)  
- ✅ Interactive `--prompt` mode (ask before updating each file, with "yes to all")  
- ✅ `--dry-run` mode to preview actions without writing  
- ✅ Logging support (`--log-file`)  

---

## Installation

### Requirements
- Python 3.7+  
- [mutagen](https://mutagen.readthedocs.io/)  
- [requests](https://docs.python-requests.org/)  

Install dependencies with:

```bash
pip install mutagen requests
```

---

## Usage

Run the script with Python:

```bash
python flac_lyrics.py <directory>
```

### Options

| Option         | Description |
|----------------|-------------|
| `--force`      | Overwrite existing `.lrc` files and `LYRICS` tags if lyrics are found |
| `--prompt`     | Ask before writing changes for each file (includes "yes to all" option) |
| `--dry-run`    | Show what would happen without making changes |
| `--log-file`   | Save log output to a file. Pass a filename (e.g. `lyrics.log`) or use with no argument to auto-generate a timestamped log file |

---

### Examples

**Basic scan (no overwrites):**
```bash
python flac_lyrics.py "D:\MyMusic\FLAC"
```

**Force overwrite existing lyrics:**
```bash
python flac_lyrics.py "D:\MyMusic\FLAC" --force
```

**Interactive mode (ask before updating each file):**
```bash
python flac_lyrics.py "D:\MyMusic\FLAC" --prompt
```

**Preview only (no changes written):**
```bash
python flac_lyrics.py "D:\MyMusic\FLAC" --dry-run
```

**Write log to file automatically:**
```bash
python flac_lyrics.py "D:\MyMusic\FLAC" --log-file
```

**Write log to specific file:**
```bash
python flac_lyrics.py "D:\MyMusic\FLAC" --log-file lyrics.log
```

---

## Notes
- Works on **Windows**, **Linux**, and **macOS**.  
- On Windows, always run with `python flac_lyrics.py ...`. On Linux/macOS, you can also make it executable (`chmod +x flac_lyrics.py`).  
- Only `.flac` files are supported in this version.  

---

## License
MIT License — feel free to use and modify.
