"""Distribution invariants; semantic writing quality is evaluated separately."""
import hashlib
import importlib.util
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
import unittest
from urllib.parse import unquote, urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('release', ROOT / 'scripts/build_release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


def check_links(folder):
    errors = []
    for path in folder.rglob('*.md'):
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            parsed = urlsplit(link.strip('<>'))
            if parsed.scheme or not parsed.path:
                continue
            target = (path.parent / unquote(parsed.path)).resolve()
            if folder.resolve() not in target.parents or not target.is_file():
                errors.append((str(path.relative_to(folder)), link))
    return errors


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='video-script-')
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.zip_path = self.folder / 'skill.zip'

    def unpack(self):
        release.build(self.zip_path)
        with zipfile.ZipFile(self.zip_path) as archive:
            archive.extractall(self.folder / 'installed')
        return self.folder / 'installed' / release.SLUG

    def test_entry_name_and_required_frontmatter(self):
        entry = (ROOT / 'skills' / release.SLUG / 'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(entry.startswith('---\n'))
        frontmatter, body = entry[4:].split('\n---\n', 1)
        fields = dict(line.split(': ', 1) for line in frontmatter.splitlines())
        self.assertEqual(fields['name'], release.SLUG)
        self.assertGreater(len(fields['description']), 30)
        self.assertNotIn('TODO', body)

    def test_source_and_installed_links_resolve(self):
        self.assertEqual(check_links(ROOT), [])
        self.assertEqual(check_links(self.unpack()), [])

    def test_zip_has_one_direct_skill_root(self):
        installed = self.unpack()
        self.assertTrue((installed / 'SKILL.md').is_file())
        with zipfile.ZipFile(self.zip_path) as archive:
            names = archive.namelist()
            self.assertEqual(set(names), {release.SLUG + '/' + n for n in release.FILES.values()})
            self.assertTrue(all('..' not in PurePosixPath(n).parts for n in names))
            self.assertEqual(len(names), len(set(names)))

    def test_core_source_bytes_equal_installed_bytes(self):
        installed = self.unpack()
        for name in release.SKILL_FILES:
            self.assertEqual((ROOT / 'skills' / release.SLUG / name).read_bytes(),
                             (installed / name).read_bytes(), name)

    def test_rebuild_is_byte_identical(self):
        release.build(self.zip_path)
        second = self.folder / 'second.zip'
        release.build(second)
        self.assertEqual(self.zip_path.read_bytes(), second.read_bytes())

    def test_sha256_matches_actual_zip(self):
        result = release.build(self.zip_path)
        digest = hashlib.sha256(self.zip_path.read_bytes()).hexdigest()
        self.assertEqual(result['sha256'], digest)
        self.assertEqual(self.zip_path.with_suffix('.zip.sha256').read_text(encoding='utf-8'),
                         digest + '  skill.zip\n')

    def test_existing_output_is_preserved(self):
        self.zip_path.write_bytes(b'original')
        with self.assertRaises(ValueError):
            release.build(self.zip_path)
        self.assertEqual(self.zip_path.read_bytes(), b'original')

    def test_existing_checksum_is_preserved(self):
        checksum = self.zip_path.with_suffix('.zip.sha256')
        checksum.write_bytes(b'original')
        with self.assertRaises(ValueError):
            release.build(self.zip_path)
        self.assertFalse(self.zip_path.exists())
        self.assertEqual(checksum.read_bytes(), b'original')

    def test_unlisted_private_file_is_not_packed(self):
        clone = self.folder / 'source'
        shutil.copytree(ROOT, clone, ignore=shutil.ignore_patterns('.git', '__pycache__', 'dist'))
        (clone / 'private-notes.txt').write_text('not for distribution', encoding='utf-8')
        original = release.ROOT
        release.ROOT = clone
        try:
            release.build(self.zip_path)
        finally:
            release.ROOT = original
        with zipfile.ZipFile(self.zip_path) as archive:
            self.assertFalse(any('private-notes' in n for n in archive.namelist()))

    def test_source_symlink_rejected_before_output(self):
        clone = self.folder / 'source'
        shutil.copytree(ROOT, clone, ignore=shutil.ignore_patterns('.git', '__pycache__', 'dist'))
        target = clone / 'README.md'
        target.unlink()
        external = self.folder / 'external.md'
        external.write_text('private', encoding='utf-8')
        try:
            target.symlink_to(external)
        except OSError:
            self.skipTest('host does not allow creating symlinks')
        original = release.ROOT
        release.ROOT = clone
        try:
            with self.assertRaises(ValueError):
                release.build(self.zip_path)
        finally:
            release.ROOT = original
        self.assertFalse(self.zip_path.exists())

    def test_released_text_has_no_machine_or_business_dependencies(self):
        installed = self.unpack()
        banned = ('/Users/', 'Hanxu-Business-System', 'content_workflow_v3_runtime.py',
                  'workflow_quality_gate.py', 'AUTO_CONTINUE_SAME_TURN', 'source_media_ref',
                  'sk-proj-')
        for path in installed.rglob('*'):
            if path.is_file():
                text = path.read_text(encoding='utf-8')
                for marker in banned:
                    self.assertNotIn(marker, text, str(path))

    def test_ui_metadata_is_consistent(self):
        text = (ROOT / 'skills' / release.SLUG / 'agents/openai.yaml').read_text(encoding='utf-8')
        self.assertIn('$' + release.SLUG, text)
        self.assertNotIn('allow_implicit_invocation: false', text)
        short = re.search(r'short_description: "(.+)"', text).group(1)
        self.assertTrue(25 <= len(short) <= 64)

    def test_version_is_consistent(self):
        for name in ('README.md', 'INSTALL.md'):
            text = (ROOT / name).read_text(encoding='utf-8')
            self.assertIn('/tree/v' + release.VERSION + '/', text)
            self.assertIn(release.SLUG + '-v' + release.VERSION + '.zip', text)
        text = (ROOT / 'skills' / release.SLUG / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('版本：' + release.VERSION, text)

    def test_instruction_only_install_needs_no_executable(self):
        installed = self.unpack()
        self.assertFalse(any(p.suffix in ('.py', '.js', '.sh', '.exe') for p in installed.rglob('*')))
        self.assertFalse((installed / 'requirements.txt').exists())
        self.assertFalse((installed / 'package.json').exists())


if __name__ == '__main__':
    unittest.main()
