#!/usr/bin/env python3
"""
flac_lyrics.py
==============

This script scans a folder (and subfolders) for FLAC music files.  
For each file, it will:
  1. Query the lrclib.net API for synced lyrics.
  2. If found, create a `.lrc` file with the same name as the music file.
  3. Embed the lyrics inside the FLAC file’s `LYRICS` tag.

Usage:
------

# Basic (scan folder for FLAC files):
    python flac_lyrics.py "D:\MyMusic\FLAC"

# Force overwrite existing lyrics and LRC files:
    python flac_lyrics.py "D:\MyMusic\FLAC" --force

# Prompt mode (ask before writing to each file, with "yes to all" option):
    python flac_lyrics.py "D:\MyMusic\FLAC" --prompt

# Dry run (show what would happen, make no changes):
    python flac_lyrics.py "D:\MyMusic\FLAC" --dry-run

# Save log output automatically (timestamped file):
    python flac_lyrics.py "D:\MyMusic\FLAC" --log-file

# Save log output to specific file:
    python flac_lyrics.py "D:\MyMusic\FLAC" --log-file lyrics.log

Dependencies:
-------------
- Python 3.7+
- `mutagen` (for FLAC tag editing)
- `requests` (for API calls)

Install dependencies with:
    pip install mutagen requests
"""

import os
import sys
import argparse
import requests
from mutagen.flac import FLAC
from datetime import datetime

# ----------------------------------------------------------
# Query lrclib.net API for synced lyrics
# ----------------------------------------------------------
def fetch_lyrics(artist, title):
    url = "https://lrclib.net/api/get"
    try:
        response = requests.get(url, params={"artist_name": artist, "track_name": title}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("syncedLyrics"):
                return data["syncedLyrics"]
            elif data.get("plainLyrics"):
                return data["plainLyrics"]
    except Exception as e:
        return None
    return None


# ----------------------------------------------------------
# Write lyrics to a .lrc file in the same folder
# ----------------------------------------------------------
def write_lrc_file(music_file, lyrics, force):
    lrc_path = os.path.splitext(music_file)[0] + ".lrc"
    if os.path.exists(lrc_path) and not force:
        return False  # already exists
    with open(lrc_path, "w", encoding="utf-8") as f:
        f.write(lyrics)
    return True


# ----------------------------------------------------------
# Embed lyrics into the FLAC file's metadata
# ----------------------------------------------------------
def embed_lyrics_flac(music_file, lyrics, force):
    try:
        audio = FLAC(music_file)
        if "LYRICS" in audio and not force:
            return False  # already has lyrics
        audio["LYRICS"] = lyrics
        audio.save()
        return True
    except Exception:
        return False


# ----------------------------------------------------------
# Process one FLAC file: check, fetch, write, embed
# ----------------------------------------------------------
def process_file(path, args, yes_to_all):
    try:
        audio = FLAC(path)
    except Exception:
        return (path, "error")

    artist = audio.get("artist", [None])[0]
    title = audio.get("title", [None])[0]

    if not artist or not title:
        return (path, "missing_tags")

    lrc_path = os.path.splitext(path)[0] + ".lrc"
    has_lrc = os.path.exists(lrc_path)
    has_tag = "LYRICS" in audio

    # Skip if lyrics already exist and not forcing
    if (has_lrc or has_tag) and not args.force and not args.prompt:
        return (path, "skipped_existing")

    # Fetch lyrics
    lyrics = fetch_lyrics(artist, title)
    if not lyrics:
        return (path, "not_found")

    # Prompt mode: ask before writing
    if args.prompt and not yes_to_all[0]:
        while True:
            ans = input(f"Update lyrics for '{artist} - {title}'? [y/n/a] ").strip().lower()
            if ans == "a":  # yes to all
                yes_to_all[0] = True
                break
            elif ans == "y":
                break
            elif ans == "n":
                return (path, "skipped_prompt")
            else:
                print("Please type y (yes), n (no), or a (yes to all).")

    if args.dry_run:
        return (path, "dry_run")

    wrote_file = write_lrc_file(path, lyrics, args.force)
    wrote_tag = embed_lyrics_flac(path, lyrics, args.force)

    if wrote_file or wrote_tag:
        return (path, "updated")

    return (path, "skipped_existing")


# ----------------------------------------------------------
# Main function: walk directory and process files
# ----------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Fetch and embed synced lyrics into FLAC files")
    parser.add_argument("directory", help="Folder containing FLAC files")
    parser.add_argument("--force", action="store_true", help="Overwrite existing lyrics and LRC files")
    parser.add_argument("--prompt", action="store_true", help="Ask before updating each file")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without writing changes")
    parser.add_argument("--log-file", nargs="?", const="AUTO", help="Write log output to a file")
    args = parser.parse_args()

    log_lines = []
    yes_to_all = [False]  # state shared with process_file

    for root, _, files in os.walk(args.directory):
        for f in files:
            if f.lower().endswith(".flac"):
                full_path = os.path.join(root, f)
                print(f"Processing: {full_path}")
                status = process_file(full_path, args, yes_to_all)
                line = f"{status[0]}: {status[1]}"
                log_lines.append(line)
                print("  ->", status[1])

    # Summary
    print("\n--- Summary ---")
    for line in log_lines:
        print(line)

    # Log file output
    if args.log_file:
        if args.log_file == "AUTO":
            filename = f"lyrics_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        else:
            filename = args.log_file
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines))
        print(f"\nLog written to {filename}")


if __name__ == "__main__":
    main()
