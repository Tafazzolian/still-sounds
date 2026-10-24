#!/usr/bin/env python3
"""Encodes a 48 kHz loop as Ogg Opus that repeats without a click: python3 loop-opus.py loop.wav out.ogg 64k

Opus encodes 20 ms frames (960 samples) after a pre-skip the decoder drops (312). Encoded plainly, a loop clicks at
every repeat (brown noise: 9 to 20 dB more highs on the seam than anywhere in the sound): the encoder starts from
silence, and that onset sprays highs over the first milliseconds; the last frame is padded with silence; and a player
that does not trim the end (the app's Media3 1.11 does not: its Ogg Opus reader reads no end trim) plays that padding
too, up to 20 ms. So the encoder gets the loop's end before its start (about 100 ms, dropped with the pre-skip, which
grows by as much) and the loop's start again after its end, as the sound really goes on, and the file is cut on a frame
boundary so there is nothing to trim. And a loop of whole frames (make-loop.sh cuts them so) is encoded the same on both
sides of the seam: its start falls on the same place in a frame, after the same audio, at the file's start and after
its end, so the codec's small errors match too (a loop of 2,879,688 samples still clicked, +14 dB; 2,880,000 did not).
"""
import os, struct, subprocess, sys, tempfile

FRAME, LOOKAHEAD, AFTER = 960, 312, 2 * 960
WARM = int(os.environ.get("WARM", "4"))

def crc32(data):
    crc = 0
    for b in data:
        crc ^= b << 24
        for _ in range(8):
            crc = ((crc << 1) ^ 0x04C11DB7) & 0xFFFFFFFF if crc & 0x80000000 else (crc << 1) & 0xFFFFFFFF
    return crc

def pages(data):
    i = 0
    while i < len(data):
        assert data[i:i + 4] == b"OggS", "not an Ogg page"
        n = data[i + 26]
        table = list(data[i + 27:i + 27 + n])
        body = data[i + 27 + n:i + 27 + n + sum(table)]
        yield {"type": data[i + 5], "granule": struct.unpack("<q", data[i + 6:i + 14])[0], "head": data[i:i + 27], "table": table, "body": body}
        i += 27 + n + sum(table)

def build(p):
    head = bytearray(p["head"])
    head[5] = p["type"]
    head[6:14] = struct.pack("<q", p["granule"])
    head[22:26] = b"\0\0\0\0"
    head[26] = len(p["table"])
    page = bytes(head) + bytes(p["table"]) + p["body"]
    return page[:22] + struct.pack("<I", crc32(page)) + page[26:]

def main():
    src, out, rate = sys.argv[1], sys.argv[2], sys.argv[3]
    n = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=duration_ts", "-of", "csv=p=0", src],
                           capture_output=True, text=True, check=True).stdout)
    if n % FRAME:
        print(f"{out}: {n} samples, not whole 20 ms frames ({n // FRAME * FRAME} or {(n // FRAME + 1) * FRAME} would be): the seam may click", file=sys.stderr)
    before = (-LOOKAHEAD - n) % FRAME + WARM * FRAME
    keep = (LOOKAHEAD + before + n) // FRAME
    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, "raw.ogg")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-stream_loop", "2", "-i", src,
                        "-af", f"atrim=start_sample={n - before}:end_sample={2 * n + AFTER},asetpts=PTS-STARTPTS",
                        "-c:a", "libopus", "-b:a", rate, "-vbr", "on", "-application", "audio", "-frame_duration", "20", raw], check=True)
        data = open(raw, "rb").read()
    result, packets = [], 0
    for k, p in enumerate(pages(data)):
        if k == 0:
            assert p["body"][:8] == b"OpusHead"
            skip = struct.unpack("<H", p["body"][10:12])[0]
            assert skip == LOOKAHEAD, f"pre-skip {skip}, expected {LOOKAHEAD}"
            p["body"] = p["body"][:10] + struct.pack("<H", skip + before) + p["body"][12:]
        elif k == 1:
            assert p["body"][:8] == b"OpusTags" and p["table"][-1] < 255
        else:
            assert not p["type"] & 1 and p["table"][-1] < 255, "a packet across pages"
            ends = [i for i, v in enumerate(p["table"]) if v < 255]
            if packets + len(ends) >= keep:
                cut = ends[keep - packets - 1] + 1
                p["body"] = p["body"][:sum(p["table"][:cut])]
                p["table"] = p["table"][:cut]
                p["granule"], p["type"] = keep * FRAME, p["type"] | 4
                result.append(build(p))
                break
            packets += len(ends)
            assert p["granule"] == packets * FRAME, "packets are not all 20 ms"
        result.append(build(p))
    else:
        raise SystemExit("the encoding is shorter than the loop")
    open(out, "wb").write(b"".join(result))

if __name__ == "__main__":
    main()
