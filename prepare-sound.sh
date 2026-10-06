#!/bin/bash
# Prepares a downloaded loop for STILL: its peaks softened a little (thunder, gusts), brought to -23 LUFS with one fixed
# gain, and saved as Ogg Opus (64 kbps stereo, or 48 kbps for a mono source) in files/<id>.ogg.
#
#   ./prepare-sound.sh original.ogg storm
#
# The loop's two ends are treated like its middle: three copies are processed back to back and the middle one is kept,
# so the softening never starts fresh at the seam (done on the first sound, it left the start 3.4 dB louder than the
# end, a bump at every repeat). Needs ffmpeg with libopus. Then run make-catalog.py.
set -e
IN="$1";ID="$2"
[ -f "$IN" ] && [ -n "$ID" ] || { echo "Usage: $0 original-file sound-id"; exit 1; }
cd "$(dirname "$0")"
TMP=$(mktemp -d);trap 'rm -rf "$TMP"' EXIT
N=$(ffprobe -v error -select_streams a:0 -count_packets -show_entries stream=duration_ts -of csv=p=0 "$IN")
CH=$(ffprobe -v error -select_streams a:0 -show_entries stream=channels -of csv=p=0 "$IN")
N2=$((2*N))
ffmpeg -hide_banner -loglevel error -y -stream_loop 2 -i "$IN" \
  -af "acompressor=threshold=-26dB:ratio=3:attack=15:release=500:knee=6,atrim=start_sample=${N}:end_sample=${N2},asetpts=PTS-STARTPTS" \
  -c:a pcm_f32le "$TMP/mid.wav"
GAIN=$(ffmpeg -hide_banner -nostats -i "$TMP/mid.wav" -af ebur128 -f null - 2>&1 | grep -A3 "Integrated loudness" | grep "I:" | awk '{print -23-$2}')
RATE=$([ "$CH" = "1" ] && echo 48k || echo 64k)
ffmpeg -hide_banner -loglevel error -y -i "$TMP/mid.wav" -af "volume=${GAIN}dB" -ar 48000 -c:a libopus -b:a "$RATE" -vbr on -application audio "files/$ID.ogg"
echo "files/$ID.ogg: gain ${GAIN} dB, $(wc -c <"files/$ID.ogg") bytes"
ffmpeg -hide_banner -nostats -i "files/$ID.ogg" -af ebur128=peak=true -f null - 2>&1 | grep -A16 "Summary:" | grep -E "I:|LRA:|Peak:"
for w in "-t 0.2" "-sseof -0.2"; do ffmpeg -hide_banner -nostats $w -i "files/$ID.ogg" -af astats -f null - 2>&1 | grep "RMS level dB" | tail -1; done
echo "The two RMS levels above are the loop's start and end: within about 1 dB, the seam is even. Peak above -1 dBFS: soften more."
