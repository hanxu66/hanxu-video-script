#!/usr/bin/env python3
"""Build the installable instruction-only skill from an explicit file allowlist."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'hanxu-video-script'
VERSION = '0.1.0'
DOCS = ('README.md', 'INSTALL.md', 'USAGE.md', 'PROVENANCE.md',
        'RELEASE-STANDARD.md', 'VALIDATION.md')
SKILL_FILES = ('SKILL.md', 'LICENSE', 'agents/openai.yaml',
               'references/angle.md', 'references/structure.md',
               'references/verbatim.md', 'references/revision.md',
               'references/quality.md', 'references/output.md')
FILES = {name: name for name in DOCS}
FILES.update({'skills/' + SLUG + '/' + name: name for name in SKILL_FILES})


def read_public_file(relative):
    path = ROOT / relative
    # Reject file or directory links even when they point back into the tree.
    current = path
    while current != ROOT:
        if current.is_symlink():
            raise ValueError('release source is a symlink: ' + relative)
        current = current.parent
    if ROOT.resolve() not in path.resolve().parents or not path.is_file():
        raise ValueError('release source is not an ordinary package file: ' + relative)
    payload = path.read_bytes()
    if relative in DOCS:
        payload = payload.replace(('](skills/' + SLUG + '/').encode(), b'](')
    return payload


def build(output):
    output = Path(output).expanduser().absolute()
    digest_path = output.with_suffix(output.suffix + '.sha256')
    if output.exists() or output.is_symlink() or digest_path.exists() or digest_path.is_symlink():
        raise ValueError('output or checksum already exists; choose a new path')
    payloads = [(name, read_public_file(relative)) for relative, name in FILES.items()]
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in sorted(payloads):
            entry = zipfile.ZipInfo(SLUG + '/' + name, (2026, 10, 23, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, payload)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    with digest_path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(digest + '  ' + output.name + '\n')
    return {'path': str(output), 'sha256': digest, 'files': len(payloads), 'version': VERSION}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    print(json.dumps(build(parser.parse_args().output), ensure_ascii=False, indent=2))
