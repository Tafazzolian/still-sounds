#!/usr/bin/env python3
"""Does a loop's seam show? python3 check-loop.py file.ogg ...

The file decoded once and put twice in a row (ffmpeg's own -stream_loop reopens an Opus file and leaves a hole of its
own at the seam), high-passed at 3 kHz (where a click shows, and a dropout as a hole), in 2.5 ms
windows: the windows on the seam against all the others. A click is louder than nearly all of them, a dropout (the end
fading out, as a plainly encoded Opus loop does) quieter than nearly all. Seen first on brown noise: a plain encoding's
seam 4 dB under the quietest of the sound's own windows. Within the middle 99% of the sound's own windows, give or take
1.5 dB (a 2.5 ms window of quiet highs varies that much by itself, before any encoding): even.
"""
import math, struct, subprocess, sys

def main():
    bad = 0
    for f in sys.argv[1:]:
        once = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "48000", "-f", "s16le", "-"], capture_output=True).stdout
        hp = ["ffmpeg", "-v", "error", "-f", "s16le", "-ar", "48000", "-ac", "1", "-i", "-",
              "-af", "highpass=f=3000:poles=2,highpass=f=3000:poles=2", "-f", "s16le", "-"]
        d = subprocess.run(hp, input=once + once, capture_output=True).stdout
        x = struct.unpack("<%dh" % (len(d) // 2), d)
        n, w = len(x) // 2, 120
        def rms(i):
            s = x[max(0, i):i + w]
            return math.sqrt(sum(v * v for v in s) / len(s)) + 1e-9
        seam = [rms(n - w), rms(n - w // 2), rms(n)]
        others = sorted(rms(i) for i in range(w * 40, len(x) - w * 40, w * 3))
        lo, hi = others[len(others) // 200], others[-len(others) // 200]
        med = others[len(others) // 2]
        margin = 10 ** (1.5 / 20)
        verdict = "click" if max(seam) > hi * margin else "dropout" if min(seam) < lo / margin else "even"
        bad += verdict != "even"
        print(f"{f.split('/')[-1]:40s} seam {20 * math.log10(min(seam) / med):+5.1f} to {20 * math.log10(max(seam) / med):+5.1f} dB "
              f"(the sound's own: {20 * math.log10(lo / med):+5.1f} to {20 * math.log10(hi / med):+5.1f})  {verdict}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
