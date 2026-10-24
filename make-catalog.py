#!/usr/bin/env python3
"""Fills in STILL's ambient catalog from files/: each planned recording's and picture's size and SHA-256.

Usage: python3 make-catalog.py
The catalog is the app's still/src/main/assets/ambient/catalog.json. Since 2026-10-15 it plans every recording by
name: each sound lists its slots (file, name, weather), as "rain-soft.ogg" (Soft) under Rain; put a recording in
files/ under its slot's file name and run this. A slot with its file gets its size and checksum (the app then offers
it); one without stays planned (size 0, not offered). Licences, credits and source pages already in the catalog are
kept; what still needs one is listed. A sound's picture is files/<id>.jpg. A file in files/ that no slot names is
listed too: add a slot for it to the catalog first. A file whose name holds "default" (2026-10-24, the listener) is
its sound's default, played first when the sound starts; one a sound at most.
"""
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = os.path.join(HERE, "files")
CATALOG = os.path.join(HERE, "..", "still", "src", "main", "assets", "ambient", "catalog.json")

def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 16), b""):
            h.update(block)
    return h.hexdigest()

def main():
    with open(CATALOG, encoding="utf-8") as f:
        catalog = json.load(f)
    present = set(os.listdir(FILES)) if os.path.isdir(FILES) else set()
    known = set()
    problems = []
    for sound in catalog["sounds"]:
        sid = sound["id"]
        samples = []
        for slot in sound.get("samples", []):
            name = slot["file"]
            known.add(name)
            path = os.path.join(FILES, name)
            s = dict(slot)
            if os.path.isfile(path):
                s["bytes"] = os.path.getsize(path)
                s["sha256"] = digest(path)
                if s.get("licence") not in ("CC0", "CC-BY", "CC-BY-3.0", "Pixabay"):
                    problems.append(f"licence needed (CC0, CC-BY, CC-BY-3.0 or Pixabay): {name}")
                if s.get("licence", "").startswith("CC-BY") and not s.get("credit"):
                    problems.append(f"credit needed ({s['licence']}): {name}")
                if not s.get("source"):
                    problems.append(f"source page needed: {name}")
            else:
                s["bytes"] = 0
                s["sha256"] = ""
            s["default"] = "default" in name
            keys = ["file", "name", "bytes", "sha256", "licence", "credit", "source"] + (["weather"] if s.get("weather") else []) + (["default"] if s["default"] else [])
            samples.append({k: s.get(k, "") for k in keys})
        sound["samples"] = samples
        if sum(1 for x in samples if x.get("default")) > 1:
            problems.append(f"more than one default: {sid}")
        image = sound.get("image", "")
        known.add(image)
        path = os.path.join(FILES, image)
        if image and os.path.isfile(path):
            sound["imageBytes"] = os.path.getsize(path)
            sound["imageSha256"] = digest(path)
        else:
            sound["imageBytes"] = 0
            sound["imageSha256"] = ""
        if not any(x["bytes"] for x in samples):
            problems.append(f"no recordings yet: {sid} (shows as Soon)")
    for extra in sorted(present - known):
        if not extra.startswith("."):
            problems.append(f"not in the catalog: {extra}")
    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write("\n")
    ready = sum(1 for s in catalog["sounds"] if any(x["bytes"] for x in s["samples"]))
    total = sum(1 for s in catalog["sounds"] for x in s["samples"] if x["bytes"])
    planned = sum(len(s["samples"]) for s in catalog["sounds"])
    print(f"{ready} of {len(catalog['sounds'])} sounds ready, {total} of {planned} planned recordings in.")
    for p in problems:
        print(" -", p)
    return 0

if __name__ == "__main__":
    sys.exit(main())
