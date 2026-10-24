#!/usr/bin/env python3
"""Encodes a 48 kHz loop as Ogg Opus that repeats without a click or a jump.

  python3 loop-opus.py loop.wav out.ogg 64k      the loop (whole 20 ms frames: make-loop.sh cuts them so)
  python3 loop-opus.py --twice in.ogg out.ogg    in.ogg's packets twice in one stream, for check-loop.py

Opus encodes 20 ms frames (960 samples). A plain encoding of a loop starts from silence and is padded at its end, and
a player starts the file with a pre-skip it drops (312 samples) only when its decoder starts fresh. The app's player
(Media3 1.11 on the phone's own Opus decoder) repeats a file without starting its decoder afresh: no pre-skip is
dropped on a repeat (the listener heard a short jump each time in 0.9.140, whose files held 100 ms of warm-up in the
pre-skip), and no end is trimmed (its Ogg reader reads none).

So the file is one turn of a continuous encoding: the loop is encoded four times in a row, and the packets of the
third turn are kept, with no pre-skip and nothing to trim. Repeated, those packets are what the encoder made for the
sound going on, so a decoder that carries on across the repeat plays it seamlessly; one that starts afresh only
eases in over the first 2.5 ms (under the app's fade-in at the start). The file starts 312 samples before the
loop's own start, which is still the loop.
"""
import os, struct, subprocess, sys, tempfile

FRAME, TURNS, KEEP = 960, 4, 2

def crc32(data):
    crc = 0
    for b in data:
        crc ^= b << 24
        for _ in range(8):
            crc = ((crc << 1) ^ 0x04C11DB7) & 0xFFFFFFFF if crc & 0x80000000 else (crc << 1) & 0xFFFFFFFF
    return crc

def packets(data):
    """The Ogg stream's packets in order, and its serial number."""
    out, current, i, serial = [], b"", 0, None
    while i < len(data):
        assert data[i:i + 4] == b"OggS", "not an Ogg page"
        serial = struct.unpack("<I", data[i + 14:i + 18])[0]
        n = data[i + 26]
        table = data[i + 27:i + 27 + n]
        at = i + 27 + n
        for lace in table:
            current += data[at:at + lace]; at += lace
            if lace < 255:
                out.append(current); current = b""
        i = at
    return out, serial

def page(serial, seq, granule, kind, body_packets):
    table = b"".join(bytes([255] * (len(p) // 255) + [len(p) % 255]) for p in body_packets)
    assert len(table) <= 255
    head = b"OggS" + bytes([0, kind]) + struct.pack("<qII", granule, serial, seq) + b"\0\0\0\0" + bytes([len(table)])
    raw = head + table + b"".join(body_packets)
    return raw[:22] + struct.pack("<I", crc32(raw)) + raw[26:]

def write(path, serial, head, tags, audio):
    """An Ogg Opus file: its head (pre-skip 0), tags and audio packets, 50 to a page, each 20 ms."""
    head = head[:10] + struct.pack("<H", 0) + head[12:]
    pages = [page(serial, 0, 0, 2, [head]), page(serial, 1, 0, 0, [tags])]
    for k in range(0, len(audio), 50):
        chunk = audio[k:k + 50]
        last = k + 50 >= len(audio)
        pages.append(page(serial, len(pages), (k + len(chunk)) * FRAME, 4 if last else 0, chunk))
    open(path, "wb").write(b"".join(pages))

def toc_samples(p):
    """A packet's samples at 48 kHz, from its TOC byte (RFC 6716)."""
    config, code = p[0] >> 3, p[0] & 3
    size = [480, 960, 1920, 2880][config & 3] if config < 12 else ([480, 960][config & 1] if config < 16 else [120, 240, 480, 960][config & 3])
    frames = 1 if code == 0 else 2 if code in (1, 2) else p[1] & 0x3F
    return size * frames

def main():
    if sys.argv[1] == "--twice":
        data = open(sys.argv[2], "rb").read()
        found, serial = packets(data)
        write(sys.argv[3], serial, found[0], found[1], found[2:] * 2)
        return
    src, out, rate = sys.argv[1], sys.argv[2], sys.argv[3]
    n = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=duration_ts", "-of", "csv=p=0", src],
                           capture_output=True, text=True, check=True).stdout)
    if n % FRAME:
        raise SystemExit(f"{src}: {n} samples, not whole 20 ms frames ({n // FRAME * FRAME} or {(n // FRAME + 1) * FRAME} would be); make-loop.sh cuts them so")
    turn = n // FRAME
    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, "raw.ogg")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-stream_loop", str(TURNS - 1), "-i", src,
                        "-c:a", "libopus", "-b:a", rate, "-vbr", "on", "-application", "audio", "-frame_duration", "20", raw], check=True)
        data = open(raw, "rb").read()
    found, serial = packets(data)
    head, tags, audio = found[0], found[1], found[2:]
    assert head[:8] == b"OpusHead" and tags[:8] == b"OpusTags"
    assert all(toc_samples(p) == FRAME for p in audio), "packets are not all 20 ms"
    assert len(audio) >= (KEEP + 1) * turn, "the encoding is shorter than its turns"
    write(out, serial, head, tags, audio[KEEP * turn:(KEEP + 1) * turn])

if __name__ == "__main__":
    main()
