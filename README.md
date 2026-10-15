# STILL ambient sounds

The sounds and pictures STILL downloads for its ambient sounds (Moods tab), kept out of the app so the APK stays
light. This folder is meant to become a **public** repository (`still-sounds`): the app's repository is private, so
the app cannot download from it.

## Where to put the files

The app's catalog (`still/src/main/assets/ambient/catalog.json`) plans every recording by name. Put each file in
`files/` under its planned name; a sound's picture is `files/<id>.jpg`.

| Sound (id) | Recordings (file → name in the app) | Picture |
|---|---|---|
| Rain (`rain`) | `rain-soft.ogg` Soft · `storm.ogg` With thunder (in) · `rain-forest.ogg` In the forest | `rain.jpg` |
| Ocean (`waves`) | `ocean-waves.ogg` Waves · `ocean-beach.ogg` Beach · `ocean-ship.ogg` Old ship | `waves.jpg` |
| Night (`night`) | `night-crickets.ogg` Crickets · `night-birds.ogg` Birds · `night-city.ogg` City | `night.jpg` |
| Forest (`forest`) | `forest-stream.ogg` Stream · `forest-jungle.ogg` Jungle | `forest.jpg` |
| Fireplace (`fireplace`) | `fireplace.ogg` | `fireplace.jpg` |
| Noise (`noise`) | `noise-fan.ogg` Fan · `noise-fridge.ogg` Fridge · `noise-brown.ogg` Brown | `noise.jpg` |

The app downloads a sound's recordings together, plays one at random (never the same twice in a row), and changes to
another on next or previous; the open sound (long press) lists them by name. A recording made for a weather says so
(`"weather": "storm"` on With thunder): it draws a storm behind Now Playing, and in a storm the sound for the moment
picks it. Another recording or sound: add its slot (file, name) to the catalog first. Each recording has its own
licence, credit and page.

## The sounds

- **Ogg Opus, mono 48 kbps or stereo 64 kbps** (stereo where the width matters, as rain on headphones). About 360–480 KB
  a minute. `./prepare-sound.sh original.ogg <name>` does all of this: it softens the peaks a little, brings the sound to
  −23 LUFS with one fixed gain, keeps the loop's seam even (it processes three copies and keeps the middle one) and writes
  `files/<name>.ogg` (give the planned name without .ogg, as `rain-soft`), then shows the loudness and the seam.
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
| storm.ogg (Rain · With thunder) | [Nox_Sound, Freesound 553887](https://freesound.org/people/Nox_Sound/sounds/553887/): rain, thunder and a fire, indoors | CC0 |

## When the files are in

Run `python3 make-catalog.py`: it fills each planned recording that is in `files/` with its size and SHA-256 (the app
checks every download against them, so a changed or broken file is never used), leaves the others planned (not
offered), keeps the licences, credits and pages already there, and lists what still needs one, and files no slot names.

Then publish: create the public repository `still-sounds`, commit `files/`, tag it `v1`, and make a GitHub release
`v1` with the same files attached. The catalog lists two mirrors, tried in order: the release, then jsDelivr
(which serves the tagged files). A new set of files gets a new tag (`v2`) and the catalog's mirrors move to it.
