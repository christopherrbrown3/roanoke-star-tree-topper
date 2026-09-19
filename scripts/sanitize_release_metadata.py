"""Remove local-path render metadata without changing pixels or mesh data."""
import json
from pathlib import Path
import shutil
import struct
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'print_in_place'


def png_chunks(data):
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    offset = 8
    while offset < len(data):
        size = struct.unpack('>I', data[offset:offset+4])[0]
        end = offset + size + 12
        yield data[offset+4:offset+8], data[offset:end]
        offset = end
    assert offset == len(data)


changed_previews = []
for path in sorted((OUT / 'previews').glob('*.png')):
    original = path.read_bytes()
    chunks = list(png_chunks(original))
    cleaned = original[:8] + b''.join(
        data for kind, data in chunks
        if kind not in (b'tEXt', b'zTXt', b'iTXt', b'eXIf'))
    assert [data for kind, data in chunks if kind == b'IDAT'] == [
        data for kind, data in png_chunks(cleaned) if kind == b'IDAT']
    if cleaned != original:
        path.write_bytes(cleaned)
        changed_previews.append(path.name)

blend = OUT / 'roanoke_star_A1.blend'
original = blend.read_bytes()
compressed = not original.startswith(b'BLENDER')
zstd = shutil.which('zstd')
if compressed:
    if zstd is None:
        raise RuntimeError('Install zstd to sanitize the compressed Blender file.')
    raw = subprocess.run([zstd, '-d', '-c'], input=original,
                         capture_output=True, check=True).stdout
else:
    raw = original
assert raw.startswith(b'BLENDER')
home = str(Path.home()).encode()
replacement = b'/source'.ljust(len(home), b'_')
assert len(replacement) == len(home)
cleaned = raw.replace(home, replacement)
assert len(cleaned) == len(raw)
assert home not in cleaned
if cleaned != raw:
    if compressed:
        output = subprocess.run([zstd, '-q', '-c', '-3'], input=cleaned,
                                capture_output=True, check=True).stdout
        verified = subprocess.run([zstd, '-d', '-c'], input=output,
                                  capture_output=True, check=True).stdout
        assert verified == cleaned
    else:
        output = cleaned
    blend.write_bytes(output)

with zipfile.ZipFile(OUT / 'roanoke_star_A1.3mf') as archive:
    for name in archive.namelist():
        data = archive.read(name)
        assert home not in data, f'Local path in 3MF entry {name}'
        assert b'DesignerUserId' not in data, f'Account ID in 3MF entry {name}'
        assert b'privaterelay.appleid.com' not in data

print(json.dumps({
    'preview_metadata_removed': changed_previews,
    'preview_image_data_unchanged': True,
    'blend_local_paths_removed': cleaned != raw,
    'blend_changes_are_same_length_path_substitutions_only': True,
    'package_privacy_check_passed': True,
}, indent=2))
