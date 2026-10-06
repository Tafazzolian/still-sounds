#!/usr/bin/env python3
"""Fills in the size and SHA-256 of every ambient sound and picture in STILL's catalog, from files/.

Usage: python3 make-catalog.py
The catalog is the app's still/src/main/assets/ambient/catalog.json; names, licences and credits are kept.
"""
import hashlib, json, os, sys

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
        for name_key, bytes_key, sha_key in (("file", "bytes", "sha256"), ("image", "imageBytes", "imageSha256")):
            name = sound.get(name_key, "")
            known.add(name)
            path = os.path.join(FILES, name)
            if name and os.path.isfile(path):
                sound[bytes_key] = os.path.getsize(path)
                sound[sha_key] = digest(path)
            else:
                sound[bytes_key] = 0
                sound[sha_key] = ""
                problems.append(f"missing: {name} ({sound['id']})")
        if sound.get("licence") == "CC-BY" and not sound.get("credit"):
            problems.append(f"credit needed (CC-BY): {sound['id']}")
        if sound.get("sha256") and not sound.get("source"):
            problems.append(f"source page missing: {sound['id']}")
    for extra in sorted(present - known):
        if not extra.startswith("."):
            problems.append(f"not in the catalog: {extra}")
    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write("\n")
    ready = sum(1 for s in catalog["sounds"] if s["sha256"])
    print(f"{ready} of {len(catalog['sounds'])} sounds ready.")
    for p in problems:
        print(" -", p)
    return 0

if __name__ == "__main__":
    sys.exit(main())
