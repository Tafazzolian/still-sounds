# STILL ambient sounds

The sounds and pictures STILL downloads for its ambient sounds (Moods tab), kept out of the app so the APK stays
light. This folder is meant to become a **public** repository (`still-sounds`): the app's repository is private, so
the app cannot download from it.

## Where to put the files

The app's catalog (`still/src/main/assets/ambient/catalog.json`) plans every recording by name. Put each file in
`files/` under its planned name; a sound's picture is `files/<id>.jpg`.

| Sound (id) | Recordings (file → name in the app; **default** plays first) | Picture |
|---|---|---|
| Rain (`rain`) | **`rain-distant-thunder-default-garybran.ogg` Distant thunder (storm)** · `rain-soft.ogg` Soft · `rain-rooftop-simonspiers.ogg` On the rooftop | `rain.jpg` (Colin Lloyd (Unsplash)) |
| Ocean (`waves`) | **`ocean-beach-default.ogg` Beach** · `ocean-ship-seagulls.ogg` Ship and seagulls · `ocean-waves.ogg` Waves | `waves.jpg` (Mark Kassinos (Unsplash)) |
| Night (`night`) | **`night-crickets-default.ogg` Crickets** · `night-crickets.ogg` Back porch · `night-city.ogg` City | `night.jpg` (Unsplash) |
| Forest (`forest`) | **`forest-birds-default.ogg` Nightingale** · `forest-birds.ogg` Spring birds · `forest-rain.ogg` Rain · `forest-river.ogg` River · `forest-stream.ogg` Stream | `forest.jpg` (Andrew A (Unsplash)) |
| Fireplace (`fireplace`) | **`fireplace-lit-default.ogg` Lit fireplace** · `fireplace-crackling.ogg` Crackling · `fireplace-bonfire.ogg` Bonfire · `fireplace-rain.ogg` Rain outside | `fireplace.jpg` (Karel Mistrik (Unsplash)) |
| Noise (`noise`) | **`noise-brown-default.ogg` Brown** · `noise-fridge.ogg` Fridge · `noise-old-clock.ogg` Old clock · `noise-street.ogg` Street · `noise-wind.ogg` Wind · `noise-fan.ogg` Fan · `noise-large-fan.ogg` Large fan | `noise.jpg` (Jeremy Bishop (Unsplash)) |

The app downloads a sound's recordings together, plays its default first (the file named `-default`; make-catalog.py marks it), then another at random on next or previous (never the same twice in a row); the open sound (long press) lists them by name. A recording made for a weather says so
(`"weather": "storm"` on Distant thunder): in a storm the sound for the moment picks it. Another recording or sound: add its slot (file, name) to the catalog first. Each recording has its own
licence, credit and page.

## The sounds

- **Ogg Opus, mono 48 kbps or stereo 64 kbps** (stereo where the width matters, as rain on headphones). About 360–480 KB
  a minute. `./prepare-sound.sh original.ogg <name>` does all of this: it softens the peaks a little, brings the sound to
  −23 LUFS with one fixed gain, keeps the loop's seam even (it processes three copies and keeps the middle one) and writes
  `files/<name>.ogg` (give the planned name without .ogg, as `rain-soft`), then shows the loudness and the seam.
  A longer recording that is not a loop yet: `./make-loop.sh original.wav rain-soft [seconds] [calm|storm]` cuts its
  most even minute (`pick-loop.py`), cross-fades the end into the start and runs `prepare-sound.sh` on it.
- **The seam**: a plainly encoded Opus loop clicks, drops out or jumps at every repeat: the encoder starts from
  silence and pads the end, and the app's player repeats a file without starting its decoder afresh, so it drops no
  pre-skip and trims no end on a repeat (v2 kept 100 ms of warm-up in the pre-skip, heard as a short jump each time).
  `loop-opus.py`, run by `prepare-sound.sh`, encodes the loop four times in a row and keeps the third turn's packets,
  with no pre-skip and nothing to trim, so repeated they are what the encoder made for the sound going on. The loop
  must be whole 20 ms frames (960 samples), as `make-loop.sh` cuts them. `python3 check-loop.py files/*.ogg` plays
  each file twice as the app does and says whether the seam is even, clicks or drops out.
- **30–90 seconds, made to loop**: the end runs into the start without a click or a change in level (in Audacity:
  cross-fade the last two seconds into the first two, then cut). The app repeats the file.
- **Even loudness**: normalise every file to about −23 LUFS so no sound is much louder than another.
- **Licence**: CC0 is simplest (Freesound: Licence → "Creative Commons 0"). CC-BY works too, with the author's name
  in `credit`. Never CC-BY-NC (no commercial use) or the BBC archive (non-commercial). Keep the page address in
  `source` for every file.

## The pictures

- **Portrait JPEG, the long side at most 1600 px, quality about 80** (50–280 KB), metadata stripped: `files/<id>.jpg`.
  Shown behind Now Playing while the sound plays (center-cropped, so in landscape its middle band; the night's stars
  over Night's), and in the notification and on the lock screen. The photographer goes in the catalog's `imageCredit`.
  Unsplash's licence is fine (free, commercial use, no credit required); otherwise the same rules as the sounds.

## The sounds so far

| File | Source | Licence |
|---|---|---|
| rain-distant-thunder-default-garybran.ogg (Rain · Distant thunder) | [GaryBran, Freesound 76685](https://freesound.org/people/GaryBran/sounds/76685/) | CC0 |
| rain-soft.ogg (Rain · Soft) | [mshahen, Freesound 242894](https://freesound.org/people/mshahen/sounds/242894/) | CC-BY |
| rain-rooftop-simonspiers.ogg (Rain · On the rooftop) | [Simon Spiers, Freesound 394600](https://freesound.org/people/Simon%20Spiers/sounds/394600/) | CC0 |
| ocean-beach-default.ogg (Ocean · Beach) | [InspectorJ, Freesound 400632](https://freesound.org/people/InspectorJ/sounds/400632/) | CC-BY |
| ocean-ship-seagulls.ogg (Ocean · Ship and seagulls) | [LXX.70, Freesound 91072](https://freesound.org/people/LXX.70/sounds/91072/) | CC-BY |
| ocean-waves.ogg (Ocean · Waves) | [Noted451, Freesound 531015](https://freesound.org/people/Noted451/sounds/531015/) | CC0 |
| night-crickets-default.ogg (Night · Crickets) | [InspectorJ, Freesound 352514](https://freesound.org/people/InspectorJ/sounds/352514/) | CC-BY |
| night-crickets.ogg (Night · Back porch) | [hdfreema, Freesound 333221](https://freesound.org/people/hdfreema/sounds/333221/) | CC0 |
| night-city.ogg (Night · City) | [slag777, Freesound 167359](https://freesound.org/people/slag777/sounds/167359/) | CC-BY |
| forest-birds-default.ogg (Forest · Nightingale) | [Vonora, Freesound 269570](https://freesound.org/people/Vonora/sounds/269570/) | CC0 |
| forest-birds.ogg (Forest · Spring birds) | [BurghRecords, Freesound 463903](https://freesound.org/people/BurghRecords/sounds/463903/) | CC0 |
| forest-rain.ogg (Forest · Rain) | [INNORECORDS, Freesound 457447](https://freesound.org/people/INNORECORDS/sounds/457447/) | CC0 |
| forest-river.ogg (Forest · River) | [Glaneur de sons, Freesound 24511](https://freesound.org/people/Glaneur%20de%20sons/sounds/24511/) | CC-BY |
| forest-stream.ogg (Forest · Stream) | [jackthemurray, Freesound 433589](https://freesound.org/people/jackthemurray/sounds/433589/) | CC0 |
| fireplace-lit-default.ogg (Fireplace · Lit fireplace) | [lurpsis, Freesound 444127](https://freesound.org/people/lurpsis/sounds/444127/) | CC0 |
| fireplace-crackling.ogg (Fireplace · Crackling) | [A Freesound member, Freesound 164661](https://freesound.org/people/deleted_user_2104797/sounds/164661/) | CC0 |
| fireplace-bonfire.ogg (Fireplace · Bonfire) | [forfie, Freesound 364992](https://freesound.org/people/forfie/sounds/364992/) | CC0 |
| fireplace-rain.ogg (Fireplace · Rain outside) | [Nox_Sound, Freesound 553887](https://freesound.org/people/Nox_Sound/sounds/553887/) | CC0 |
| noise-brown-default.ogg (Noise · Brown) | [tracyradio, Freesound 737409](https://freesound.org/people/tracyradio/sounds/737409/) | CC0 |
| noise-fridge.ogg (Noise · Fridge) | [ancorapazzo, Freesound 181616](https://freesound.org/people/ancorapazzo/sounds/181616/) | CC-BY |
| noise-old-clock.ogg (Noise · Old clock) | [straget, Freesound 405423](https://freesound.org/people/straget/sounds/405423/) | CC-BY |
| noise-street.ogg (Noise · Street) | [InspectorJ, Freesound 398159](https://freesound.org/people/InspectorJ/sounds/398159/) | CC-BY |
| noise-wind.ogg (Noise · Wind) | [Glaneur de sons, Freesound 104952](https://freesound.org/people/Glaneur%20de%20sons/sounds/104952/) | CC-BY |
| noise-fan.ogg (Noise · Fan) | [lllBabaBooeylll, Freesound 536942](https://freesound.org/people/lllBabaBooeylll/sounds/536942/) | CC0 |
| noise-large-fan.ogg (Noise · Large fan) | [FOSSarts, Freesound 761929](https://freesound.org/people/FOSSarts/sounds/761929/) | CC0 |

## When the files are in

Run `python3 make-catalog.py`: it fills each planned recording that is in `files/` with its size and SHA-256 (the app
checks every download against them, so a changed or broken file is never used), leaves the others planned (not
offered), keeps the licences, credits and pages already there, and lists what still needs one, and files no slot names.

Then publish: create the public repository `still-sounds`, commit `files/`, tag it `v1`, and make a GitHub release
`v1` with the same files attached (the catalog is on `v6` since 2026-10-26: three new fireplace recordings, the old one gone). The catalog lists two mirrors, tried in order: the release, then jsDelivr
(which serves the tagged files). A new set of files gets a new tag (`v2`) and the catalog's mirrors move to it.
