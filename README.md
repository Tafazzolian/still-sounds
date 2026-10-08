# STILL ambient sounds

The sounds and pictures STILL downloads for its ambient sounds (Moods tab), kept out of the app so the APK stays
light. This folder is meant to become a **public** repository (`still-sounds`): the app's repository is private, so
the app cannot download from it.

## Where to put the files

Put each sound and its picture in `files/`, named by the sound's id (see the app's
`still/src/main/assets/ambient/catalog.json`):

```
files/rain.ogg        files/rain.jpg
files/storm.ogg       files/storm.jpg
files/fireplace.ogg   files/fireplace.jpg
files/wind.ogg        files/wind.jpg
files/birds.ogg       files/birds.jpg
files/night.ogg       files/night.jpg
files/waves.ogg       files/waves.jpg
files/stream.ogg      files/stream.jpg
files/noise.ogg       files/noise.jpg
```

A sound can have several recordings: `storm.ogg`, `storm-2.ogg`, `storm-3.ogg`, ... The app downloads them all
together, shows how many it has under the tile, plays one at random (never the same twice in a row) and changes to
another on next or previous. Each recording has its own licence, credit and page in the catalog.

A new sound: any short id (lowercase letters, digits, dashes), added to the catalog with its name.

## The sounds

- **Ogg Opus, mono 48 kbps or stereo 64 kbps** (stereo where the width matters, as rain on headphones). About 360–480 KB
  a minute. `./prepare-sound.sh original.ogg <id>` does all of this: it softens the peaks a little, brings the sound to
  −23 LUFS with one fixed gain, keeps the loop's seam even (it processes three copies and keeps the middle one) and writes
  `files/<id>.ogg`, then shows the loudness and the seam.
- **30–90 seconds, made to loop**: the end runs into the start without a click or a change in level (in Audacity:
  cross-fade the last two seconds into the first two, then cut). The app repeats the file.
- **Even loudness**: normalise every file to about −23 LUFS so no sound is much louder than another.
- **Licence**: CC0 is simplest (Freesound: Licence → "Creative Commons 0"). CC-BY works too, with the author's name
  in `credit`. Never CC-BY-NC (no commercial use) or the BBC archive (non-commercial). Keep the page address in
  `source` for every file.

## The pictures

- **Square JPEG, 512 × 512, quality about 80** (50–80 KB). Shown as the sound's album art in Now Playing, the
  notification and on the lock screen. Same licence rules as the sounds.

## The sounds so far

| File | Source | Licence |
|---|---|---|
| storm.ogg | [Nox_Sound, Freesound 553887](https://freesound.org/people/Nox_Sound/sounds/553887/): rain, thunder and a fire, indoors | CC0 |

## When the files are in

Run `python3 make-catalog.py`: it adds each sound's recordings to the app's catalog with their size and SHA-256 (the
app checks every download against them, so a changed or broken file is never used), keeps the licences, credits and
pages already there, and lists what still needs one, and files that are unknown.

Then publish: create the public repository `still-sounds`, commit `files/`, tag it `v1`, and make a GitHub release
`v1` with the same files attached. The catalog lists two mirrors, tried in order: the release, then jsDelivr
(which serves the tagged files). A new set of files gets a new tag (`v2`) and the catalog's mirrors move to it.
