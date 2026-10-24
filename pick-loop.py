#!/usr/bin/env python3
"""Picks where to cut a loop from a longer recording: the start (seconds) of the most even stretch.

Usage: python3 pick-loop.py original length crossfade [calm|storm]
Reads the recording's momentary loudness (ffmpeg's ebur128, every 0.1 s; the first 30 minutes of a long one) and
scores each stretch of length + crossfade seconds: the two ends that make the seam should be as loud as each other and
as the stretch's middle, and (calm) no gust, car or bird call should stand out. A storm keeps its thunder: only the
seam counts. The first and last two seconds of the file are never used (fades, handling noise). Prints the start.
"""
import re, statistics, subprocess, sys

def loudness(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-t", "1800", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return [max(float(m), -70.0) for m in re.findall(r"\bM:\s*(-?[\d.]+)", out)]

def main():
    path, length, fade = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    storm = len(sys.argv) > 4 and sys.argv[4] == "storm"
    m = loudness(path)
    step, w, x, l = 10, int((length + fade) * 10), int(fade * 10), int(length * 10)
    best = None
    for s in range(20, max(21, len(m) - w - 20), 5):
        win = m[s:s + w]
        if len(win) < w:
            break
        med = statistics.median(win)
        a, b = statistics.mean(win[:x]), statistics.mean(win[l:l + x])
        score = abs(a - b) + 0.5 * (abs(a - med) + abs(b - med))
        if not storm:
            score += 0.5 * statistics.pstdev(win) + 0.2 * max(0.0, max(win) - med - 6)
        if best is None or score < best[0]:
            best = (score, s)
    print(f"{(best[1] if best else 20) / step:.1f}")

if __name__ == "__main__":
    main()
