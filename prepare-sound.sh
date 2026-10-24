#!/bin/bash
# Prepares a downloaded loop for STILL: its peaks softened a little (thunder, gusts), brought to -23 LUFS with one fixed
# gain, and saved as Ogg Opus (64 kbps stereo, or 48 kbps for a mono source) in files/<id>.ogg (OUT=folder: there).
#
#   ./prepare-sound.sh original.ogg storm
#
# The loop's two ends are treated like its middle: three copies are processed back to back and the middle one is kept,
# so the softening never starts fresh at the seam (done on the first sound, it left the start 3.4 dB louder than the
# end, a bump at every repeat). Everything is at 48 kHz, also made over three copies. The encoding (loop-opus.py) ends on
# an Opus frame, with no padding and no faded last frame. Needs ffmpeg with libopus. Then run make-catalog.py.
set -e
IN="$1";ID="$2"
[ -f "$IN" ] && [ -n "$ID" ] || { echo "Usage: $0 original-file sound-id"; exit 1; }
cd "$(dirname "$0")"
OUT="${OUT:-files}";mkdir -p "$OUT"
TMP=$(mktemp -d);trap 'rm -rf "$TMP"' EXIT
N=$(ffprobe -v error -select_streams a:0 -count_packets -show_entries stream=duration_ts -of csv=p=0 "$IN")
SR=$(ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate -of csv=p=0 "$IN")
CH=$(ffprobe -v error -select_streams a:0 -show_entries stream=channels -of csv=p=0 "$IN")
N=$(( (N*48000+SR/2)/SR ));N2=$((2*N))
ffmpeg -hide_banner -loglevel error -y -stream_loop 2 -i "$IN" \
  -af "aresample=48000,acompressor=threshold=-26dB:ratio=3:attack=15:release=500:knee=6,atrim=start_sample=${N}:end_sample=${N2},asetpts=PTS-STARTPTS" \
  -c:a pcm_f32le "$TMP/mid.wav"
# The gain, then a limiter at -2.5 dBFS (the encoding adds about 2 dB to the peaks) for what still stands out (a fire's crackle came out at +12 dBFS, clipping on
# the phone), again over three copies so it never starts fresh at the seam; the limiter takes a little loudness from a
# crackly sound, so the gain is measured once more after it.
off() { ffmpeg -hide_banner -nostats -i "$1" -af ebur128 -f null - 2>&1 | grep -A3 "Integrated loudness" | grep "I:" | awk '{print -23-$2}'; }
CEIL=0.75
limit() { ffmpeg -hide_banner -loglevel error -y -stream_loop 2 -i "$TMP/mid.wav" \
  -af "volume=$1dB,alimiter=limit=$CEIL:attack=2:release=60:level=0,atrim=start_sample=${N}:end_sample=${N2},asetpts=PTS-STARTPTS" \
  -c:a pcm_f32le "$TMP/lim.wav"; }
GAIN=$(off "$TMP/mid.wav");limit "$GAIN"
GAIN=$(awk -v a="$GAIN" -v b="$(off "$TMP/lim.wav")" 'BEGIN{print a+b}');limit "$GAIN"
RATE=$([ "$CH" = "1" ] && echo 48k || echo 64k)
encode() { python3 -I loop-opus.py "$TMP/lim.wav" "$OUT/$ID.ogg" "$RATE"; }
encode
# The encoded file is measured too: Opus drops some of a stream's or a clock's highs (1.7 dB quieter) and lifts a
# bird call's peaks (+1.1 dBFS). Up to twice: the gain corrected, and the limiter lowered when a peak is above -1 dBFS.
for pass in 1 2; do
  S=$(ffmpeg -hide_banner -nostats -i "$OUT/$ID.ogg" -af ebur128=peak=true -f null - 2>&1 | grep -A16 "Summary:")
  I=$(echo "$S" | awk '/I:/{print $2}');TP=$(echo "$S" | awk '/Peak:/{print $2}')
  awk -v i="$I" -v p="$TP" 'BEGIN{exit !((i<-23.4||i>-22.6)||p>-1)}' || break
  GAIN=$(awk -v a="$GAIN" -v i="$I" 'BEGIN{print a-23-i}')
  CEIL=$(awk -v c="$CEIL" -v p="$TP" 'BEGIN{print (p>-1)?c*10^(-(p+1.3)/20):c}')
  limit "$GAIN";encode
done
echo "$OUT/$ID.ogg: gain ${GAIN} dB, $(wc -c <"$OUT/$ID.ogg") bytes"
ffmpeg -hide_banner -nostats -i "$OUT/$ID.ogg" -af ebur128=peak=true -f null - 2>&1 | grep -A16 "Summary:" | grep -E "I:|LRA:|Peak:"
python3 -I check-loop.py "$OUT/$ID.ogg"
