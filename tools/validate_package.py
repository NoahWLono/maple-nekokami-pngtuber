#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate package integrity, exact face masks, native references and examples.

Uses only local files. Native app/online provider access is never attempted.
Run without Python's -O option so validation assertions remain enabled.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import re
import struct
import subprocess
import sys
from unittest import mock
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STATES = ['idle', 'speaking', 'blink', 'speaking-blink']
EXAMPLES = {
    'bash-fish': ('maple-bash-vs-fish-elevenlabs-voice1.mp4', 30, 1835, 14),
    'lore-intro': ('maple-lore-introduction-elevenlabs-voice1.mp4', 24, 6225, 77),
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def get_string(data, pos=0):
    size = shift = 0
    while True:
        assert pos < len(data) and shift < 35
        byte = data[pos]
        pos += 1
        size |= (byte & 127) << shift
        if not byte & 128:
            break
        shift += 7
    end = pos + size
    assert end <= len(data)
    return data[pos:end].decode('utf-8'), end


def check_assets():
    source = ROOT / 'assets/maple-original-unchanged.png'
    assert sha256(source) == 'bc25435e54e6202f7aadf2a8b00dcfe165070b55fbf3d0f910b03b51ebd6b789'
    original = np.array(Image.open(source).convert('RGBA'))
    mouth = np.array(Image.open(ROOT / 'assets/aligned/mouth-edit-mask.png')) > 0
    eyes = ((np.array(Image.open(ROOT / 'assets/aligned/eye_left-edit-mask.png')) > 0) |
            (np.array(Image.open(ROOT / 'assets/aligned/eye_right-edit-mask.png')) > 0))
    assert not np.any(mouth & eyes)
    arrays, checks = {}, {}
    expected = dict(zip(STATES, [0, 713, 2918, 3631]))
    for name, allowed in zip(STATES, [np.zeros((640, 640), bool), mouth, eyes, mouth | eyes]):
        with Image.open(ROOT / f'assets/aligned/maple-{name}.png') as image:
            assert image.size == (640, 640) and image.mode == 'RGBA'
            current = np.array(image)
        changed = np.any(original != current, axis=2)
        assert not np.any(changed & ~allowed)
        assert np.array_equal(current[:, :, 3], original[:, :, 3])
        assert int(changed.sum()) == expected[name]
        arrays[name] = current
        checks[name] = {'changed_pixels': int(changed.sum()), 'outside_mask_changes': 0, 'alpha_changes': 0}
    assert np.array_equal(arrays['speaking-blink'][mouth], arrays['speaking'][mouth])
    assert np.array_equal(arrays['speaking-blink'][eyes], arrays['blink'][eyes])
    return arrays, checks


def check_native(arrays):
    raw = (ROOT / 'project/maple-pngtuber.veado').read_bytes()
    assert raw[:9] == b'VEADOTUBE'
    pos, chunks, terminated = 9, {}, False
    while pos + 12 <= len(raw):
        identifier, kind, length = struct.unpack_from('<I4sI', raw, pos)
        pos += 12
        if identifier == 0:
            assert kind == bytes(4) and length == 0
            terminated = True
            break
        assert identifier not in chunks and pos + length <= len(raw)
        chunks[identifier] = (kind, raw[pos:pos + length])
        pos += length
    assert terminated and pos == len(raw)
    assert chunks[2][0] == b'MLST'
    assert struct.unpack('<4I', chunks[2][1]) == (3, 4, 5, 6)
    expected = [
        ('Maple Idle', [10, 10, 30, 30]),
        ('Maple Speaking', [20, 20, 40, 40]),
        ('Maple Blink', [30] * 4),
        ('Maple Speaking Blink', [40] * 4),
    ]
    for identifier, (name, refs) in enumerate(expected, 3):
        kind, data = chunks[identifier]
        assert kind == b'MSTA'
        found, cursor = get_string(data)
        assert found == name
        assert struct.unpack_from('<I', data, cursor)[0] == 2
        actual = struct.unpack_from('<8I', data, cursor + 4)
        assert list(actual) == refs + refs
        assert all(chunks[ref][0] == b'AIMG' for ref in actual)
    for name, asset_id, bitmap_id in zip(STATES, [10, 20, 30, 40], [11, 21, 31, 41]):
        kind, data = chunks[asset_id]
        assert kind == b'AIMG' and struct.unpack_from('<II', data) == (640, 640)
        assert data[8] == 1 and struct.unpack_from('<I', data, 9)[0] == bitmap_id
        kind, data = chunks[bitmap_id]
        assert kind == b'ABMP' and struct.unpack_from('<II4s', data) == (640, 640, b'RAW.')
        restored = np.frombuffer(data[12:], dtype=np.uint8).reshape(640, 640, 4)[::-1]
        assert np.array_equal(restored, arrays[name])
    return {'texture_roundtrip': 'PASS', 'state_names_and_image_slots': 'PASS', 'states': [e[0] for e in expected]}


def check_controller():
    spec = importlib.util.spec_from_file_location('statectl', ROOT / 'tools/maple_statectl.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    expected = ['/example/app', '-i', 'EXACT_INSTANCE', 'nodes', 'stateEvents', 'mini', 'set', 'Maple Speaking']
    assert module.command('/example/app', 'EXACT_INSTANCE', 'set', 'Maple Speaking') == expected
    argv = ['statectl', 'demo', '--app', '/example/app', '--instance', 'TEST', '--seconds', '0.01']
    with mock.patch.object(sys, 'argv', argv), mock.patch.object(module, 'run', side_effect=[RuntimeError('test failure'), '']) as runner:
        try:
            module.main()
        except RuntimeError:
            pass
        else:
            raise AssertionError('Controller failure was hidden')
        assert runner.call_args_list[-1].args[0][-1] == 'Maple Idle'
    with mock.patch.object(sys, 'argv', ['statectl', '--app', '/example/app', '--list-instances']), mock.patch.object(module, 'run', return_value='') as runner:
        module.main()
        assert runner.call_args.args[0] == ['/example/app', '-i']
    return 'PASS: explicit targeting, instance listing and failure cleanup (mock only)'


def check_manifest():
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
    seen = set()
    for item in manifest['files']:
        name = item['path']
        assert name not in seen and not Path(name).is_absolute() and '..' not in Path(name).parts
        seen.add(name)
        path = ROOT / name
        assert not path.is_symlink() and path.is_file(), name
        assert path.stat().st_size == item['bytes'], f'Size changed: {name}'
        assert sha256(path) == item['sha256'], f'Hash changed: {name}'
    return {'files': len(seen), 'all_sha256': 'PASS'}


def check_scripts_and_captions():
    for name, (_, _, _, count) in EXAMPLES.items():
        root = ROOT / 'examples' / name
        script = ' '.join((root / 'script.txt').read_text().split())
        meta = json.loads((root / 'timing.json').read_text())
        assert ' '.join(row['text'] for row in meta['segments']) == script
        assert ' '.join(row['text'] for row in json.loads((root / 'script.json').read_text())) == script
        assert len(meta['segments']) == count
        srt = (root / 'captions.srt').read_text()
        assert srt.count(' --> ') == count
        blocks = srt.strip().split('\n\n')
        assert ' '.join(' '.join(block.splitlines()[2:]) for block in blocks) == script
        previous_end = 0
        for row in meta['segments']:
            assert previous_end <= row['start_s'] < row['end_s'] <= meta['duration_s']
            previous_end = row['end_s']
    return 'PASS: exact script reconstruction and monotone approximate subtitle cues'


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))


def check_media():
    results = {}
    for name, (filename, fps, frames, _) in EXAMPLES.items():
        root = ROOT / 'examples' / name
        path = root / filename
        info = probe(path)
        video = next(s for s in info['streams'] if s['codec_type'] == 'video')
        audio = next(s for s in info['streams'] if s['codec_type'] == 'audio')
        assert (video['width'], video['height'], video['codec_name'], video['pix_fmt']) == (960, 720, 'h264', 'yuv420p')
        assert video['r_frame_rate'] == f'{fps}/1' and int(video['nb_frames']) == frames
        assert (audio['codec_name'], audio['sample_rate'], audio['channels']) == ('aac', '48000', 1)
        decoded = subprocess.run(['ffmpeg', '-v', 'error', '-threads', '1', '-i', str(path), '-f', 'null', '-'], capture_output=True, text=True)
        assert decoded.returncode == 0 and not decoded.stderr, name
        meta = json.loads((root / 'timing.json').read_text())
        def read_audio(p):
            return np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-threads', '1', '-i', str(p), '-ac', '1', '-ar', '48000', '-f', 'f32le', '-']), '<f4')
        encoded = read_audio(path)
        source = read_audio(root / meta['source_audio_file'])
        offset = round(48000 * meta['lead_s'])
        compare = encoded[offset:offset + len(source)]
        assert len(compare) == len(source)
        correlation = float(np.corrcoef(source, compare)[0, 1])
        assert correlation > .99 and float(np.max(np.abs(encoded))) < 1
        assert float(np.max(np.abs(encoded[round((meta['duration_s'] - .5) * 48000):]))) < .001
        results[name] = {'full_decode': 'PASS', 'frames': frames, 'duration_s': float(info['format']['duration']), 'source_audio_correlation': correlation, 'trailing_silence': 'PASS'}
        del encoded, source, compare
    preview = probe(ROOT / 'examples/four-state-preview.mp4')
    assert preview['streams'][0]['nb_frames'] == '270'
    assert preview['format']['duration'] == '9.000000'
    assert len(preview['streams']) == 1
    return results


def main():
    assert __debug__, 'Run validation without -O'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--media', action='store_true', help='Fully decode media and check speech correlation')
    args = parser.parse_args()
    arrays, asset_report = check_assets()
    report = {'result': 'PASS', 'manifest': check_manifest(), 'pixels': asset_report,
              'native_container': check_native(arrays), 'controller': check_controller(),
              'scripts_and_captions': check_scripts_and_captions(),
              'live_native_and_api': 'NOT VERIFIED', 'auditory_review': 'NOT VERIFIED'}
    if args.media:
        report['media'] = check_media()
    output = ROOT / 'build/qa/validation.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
