#!/usr/bin/env python3
"""Fills in STILL's ambient catalog from files/: each sound's recordings and picture, with their size and SHA-256.

Usage: python3 make-catalog.py
The catalog is the app's still/src/main/assets/ambient/catalog.json. A sound's recordings are files/<id>.ogg and
files/<id>-2.ogg, files/<id>-3.ogg, ... in that order; its picture is files/<id>.jpg. Names, licences, credits and
source pages already in the catalog are kept; a new recording gets empty ones to fill in (the app's build refuses a
recording without its licence and page).
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

def recordings(sound_id, present):
    """The sound's recordings in files/, the plain name first, then by number."""
    pattern = re.compile(re.escape(sound_id) + r"(?:-(\d+))?\.ogg$")
    found = [(int(m.group(1) or 1), name) for name in present for m in [pattern.fullmatch(name)] if m]
    return [name for _, name in sorted(found)]

def main():
    with open(CATALOG, encoding="utf-8") as f:
        catalog = json.load(f)
    present = set(os.listdir(FILES)) if os.path.isdir(FILES) else set()
    known = set()
    problems = []
    for sound in catalog["sounds"]:
        sid = sound["id"]
        old = {s["file"]: s for s in sound.get("samples", [])}
        samples = []
        for name in recordings(sid, present):
            known.add(name)
            path = os.path.join(FILES, name)
            s = old.get(name, {"file": name, "licence": "", "credit": "", "source": ""})
            s["bytes"] = os.path.getsize(path)
            s["sha256"] = digest(path)
            samples.append({k: s.get(k, "") for k in ("file", "bytes", "sha256", "licence", "credit", "source")})
            if s.get("licence") not in ("CC0", "CC-BY", "Pixabay"):
                problems.append(f"licence needed (CC0, CC-BY or Pixabay): {name}")
            if s.get("licence") == "CC-BY" and not s.get("credit"):
                problems.append(f"credit needed (CC-BY): {name}")
            if not s.get("source"):
                problems.append(f"source page needed: {name}")
        for gone in sorted(set(old) - {s["file"] for s in samples}):
            problems.append(f"no longer in files/, left out: {gone} ({sid})")
        sound["samples"] = samples
        image = sound.get("image", "")
        known.add(image)
        path = os.path.join(FILES, image)
        if image and os.path.isfile(path):
            sound["imageBytes"] = os.path.getsize(path)
            sound["imageSha256"] = digest(path)
        else:
            sound["imageBytes"] = 0
            sound["imageSha256"] = ""
        if not samples:
            problems.append(f"no recordings yet: {sid} (shows as Soon)")
    for extra in sorted(present - known):
        if not extra.startswith("."):
            problems.append(f"not in the catalog: {extra}")
    with open(CATALOG, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write("\n")
    ready = sum(1 for s in catalog["sounds"] if s["samples"])
    total = sum(len(s["samples"]) for s in catalog["sounds"])
    print(f"{ready} of {len(catalog['sounds'])} sounds ready, {total} recordings.")
    for p in problems:
        print(" -", p)
    return 0

if __name__ == "__main__":
    sys.exit(main())
