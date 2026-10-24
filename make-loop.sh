#!/bin/bash
# Makes a STILL loop from a longer recording, then prepares it (prepare-sound.sh): the most even stretch of about a
# minute (pick-loop.py), its last three seconds cross-faded into its first (equal power, so the seam is neither a dip
# nor a bump), at 48 kHz, mono kept mono and anything wider made stereo (a 4-channel recorder's first two channels).
#
#   ./make-loop.sh original.wav rain-soft            a minute, calm: nothing standing out
#   ./make-loop.sh original.wav storm 75 storm       75 seconds, thunder kept
#
# A recording shorter than the length gives what it has, less the cross-fade and a second at each end. Cut to the sample, in whole
# 20 ms frames (loop-opus.py: then the seam is encoded the same on both sides).
# OUT=folder writes there instead of files/.
set -e
IN="$1";ID="$2";LEN="${3:-60}";MODE="${4:-calm}";X=3
[ -f "$IN" ] && [ -n "$ID" ] || { echo "Usage: $0 original-file sound-id [seconds] [calm|storm]"; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
TMP=$(mktemp -d);trap 'rm -rf "$TMP"' EXIT
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
LEN=$(python3 -c "print(min($LEN, round($DUR-$X-2.5, 1)))")
START=$(python3 -I "$HERE/pick-loop.py" "$IN" "$LEN" "$X" "$MODE")
CH=$(ffprobe -v error -select_streams a:0 -show_entries stream=channels -of csv=p=0 "$IN")
# The two channels are not always as loud as each other. A recorder's first two of four (one rain: the right 11 dB
# lower): the quieter is brought up to the other. A file with one side all but empty, over 20 dB down (a fan: the
# left 24 dB lower, so raising it would raise only hiss): the louder side alone, as mono.
case "$CH" in 1) AF="anull";;
  *) read L R < <(ffmpeg -hide_banner -nostats -t 600 -i "$IN" -af "pan=stereo|c0=c0|c1=c1,astats=measure_overall=none:measure_perchannel=RMS_level" -f null - 2>&1 | awk '/RMS level dB/{printf "%s ", $NF}END{print ""}')
     if python3 -c "import sys; sys.exit(0 if abs($L-$R)>20 else 1)"; then AF="pan=mono|c0=c$(python3 -c "print(0 if $L>$R else 1)")"
     elif [ "$CH" = 2 ]; then AF="anull"
     else AF="pan=stereo|c0=$(python3 -c "print(10**(max(0,$R-$L)/20))")*c0|c1=$(python3 -c "print(10**(max(0,$L-$R)/20))")*c1"; fi;;
esac
NS=$(python3 -c "print(round($LEN*50)*960)");XS=$((X*48000))
ffmpeg -hide_banner -loglevel error -y -ss "$START" -t "$(python3 -c "print($LEN+$X+1)")" -i "$IN" -af "$AF,aresample=48000,atrim=end_sample=$((NS+XS))" -c:a pcm_f32le "$TMP/seg.wav"
ffmpeg -hide_banner -loglevel error -y -i "$TMP/seg.wav" -filter_complex \
  "[0]asplit[p][q];[p]atrim=start_sample=$XS,asetpts=PTS-STARTPTS[a];[q]atrim=end_sample=$XS,asetpts=PTS-STARTPTS[b];[a][b]acrossfade=ns=$XS:c1=qsin:c2=qsin" \
  -c:a pcm_f32le "$TMP/loop.wav"
[ "$(ffprobe -v error -show_entries stream=duration_ts -of csv=p=0 "$TMP/loop.wav")" = "$NS" ] || { echo "$ID: the loop is not $NS samples"; exit 1; }
echo "$ID: $NS samples ($(python3 -c "print(round($NS/48000,2))") s) from ${START} s of $(basename "$IN")"
"$HERE/prepare-sound.sh" "$TMP/loop.wav" "$ID"
