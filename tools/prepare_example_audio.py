#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regenerate a local PCM master using saved timing and static gain only.

Uses the included MP3. No network calls, account access, new synthesis,
voice conversion, pitch shift, time stretch or caption realignment.
"""
from pathlib import Path
import argparse
import json
import subprocess
import wave
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('example', choices=['bash-fish', 'lore-intro'])
    args = parser.parse_args()
    root = ROOT / 'examples' / args.example
    meta = json.loads((root / 'timing.json').read_text())
    source = root / meta['source_audio_file']
    master = root / meta['audio_file']
    master.parent.mkdir(parents=True, exist_ok=True)
    rate = meta['sample_rate']
    raw = subprocess.check_output([
        'ffmpeg', '-v', 'error', '-threads', '1', '-i', str(source),
        '-ac', '1', '-ar', str(rate), '-f', 'f32le', '-'])
    samples = np.frombuffer(raw, '<f4')
    assert np.isfinite(samples).all()
    assert abs(len(samples) / rate - meta['source_duration_s']) < 0.002
    gain = 10 ** (meta['static_gain_db'] / 20)
    processed = np.concatenate([
        np.zeros(round(rate * meta['lead_s']), dtype='float32'),
        samples * gain,
        np.zeros(round(rate * meta['tail_s']), dtype='float32')])
    assert np.max(np.abs(processed)) < 0.999
    pcm = np.round(processed * 32767).astype('<i2')
    with wave.open(str(master), 'wb') as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(pcm.tobytes())
    print(json.dumps({'example': args.example, 'master': meta['audio_file'],
                      'seconds': len(processed) / rate, 'sample_rate': rate,
                      'peak': float(np.max(np.abs(processed))),
                      'clipped_samples': int(np.sum(np.abs(pcm.astype('int32')) >= 32767))}))


if __name__ == '__main__':
    main()
