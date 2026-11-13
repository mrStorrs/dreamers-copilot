"""Exercise generated packages and the migrated installers in disposable homes."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import codex_global_instructions as global_instructions

spec = importlib.util.spec_from_file_location('build_codex', ROOT / 'scripts/build-codex.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

LEGACY = [
    'agents/bolt.toml', 'agents/forge.toml', 'agents/nova.toml', 'agents/sage.toml',
    *[f'dreamers/agents/{name}.md' for name in ('echo', 'forge', 'hone', 'nova', 'probe', 'sage', 'sentinel')],
    *[f'skills/{skill}/{file}' for skill in ('dreamers-full', 'dreamers-research') for file in ('SKILL.md', 'readme.md')],
    'dreamers/refs/hone-architecture-rubric.md', 'dreamers/refs/plan-quality.md', 'dreamers/refs/plan-selection.md',
    *[f'dreamers/templates/plan-guide-{name}.md' for name in ('selector', 'lite', 'standard', 'complex')],
    'dreamers/templates/plan-writing-guide.md',
    'dreamers/instructions/comment-rules.instructions.md', 'dreamers/instructions/git.instructions.md',
]
USER_FILES = ['config.toml', 'skills/personal/SKILL.md', 'agents/personal.toml',
              'skills/dreamers-lite/user.md', 'skills/dreamers-research/.user.md',
              'dreamers/refs/user.md', 'dreamers/agents/user.md', 'dreamers/instructions/user.md']


def run(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)


class DistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = builder.package()

    def test_catalog_source_layout_unchanged(self):
        catalog = json.loads((ROOT / '.github/catalog.json').read_text(encoding='utf-8'))
        layout = {key: [{field: row.get(field) for field in fields} for row in catalog[key]]
                  for key, fields in {'items': ('type', 'slug', 'path'),
                                      'collections': ('type', 'slug', 'readmePath', 'members'),
                                      'folderTargets': ('slug', 'sourcePath', 'destSubpath')}.items()}
        self.assertEqual(json.loads((ROOT / 'tests/fixtures/catalog-layout.json').read_text(encoding='utf-8')), layout)
        for row in catalog['items']:
            if row.get('path'):
                self.assertTrue((ROOT / row['path']).is_file(), row['path'])
        for row in catalog['collections']:
            self.assertTrue((ROOT / row['readmePath']).is_file(), row['readmePath'])
        for row in catalog['folderTargets']:
            self.assertTrue((ROOT / row['sourcePath']).is_dir())

    def test_complete_deterministic_package_and_existing_contracts(self):
        self.assertEqual(self.files, builder.package())
        source_skills = {p.parent.name for p in (ROOT / '.github/skills').glob('*/SKILL.md')}
        self.assertEqual(source_skills, {p.split('/')[1] for p in self.files if p.endswith('/SKILL.md')})
        self.assertEqual(len(list((ROOT / '.github/agents').glob('*.agent.md'))),
                         len([p for p in self.files if p.endswith('.toml')]))
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / 'package with spaces'
            run(sys.executable, str(ROOT / 'scripts/build-codex.py'), '--output', str(package))
            run(sys.executable, str(ROOT / 'tests/validate_codex_package.py'), str(package))
            self.assertEqual(self.files, {p.relative_to(package).as_posix(): p.read_text(encoding='utf-8')
                                         for p in package.rglob('*') if p.is_file()})
            marker = package / 'user.txt'
            marker.write_text('untouched', encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/build-codex.py'), '--output', str(package)], capture_output=True)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual('untouched', marker.read_text(encoding='utf-8'))

    def test_runtime_specific_behavior(self):
        for path, text in self.files.items():
            if path.endswith('/SKILL.md'):
                self.assertIn('../../dreamers/refs/codex-runtime.md', text)
                self.assertIn('../../dreamers/instructions/dreamers.instructions.md', text)
                self.assertNotIn('argument-hint:', text)
            if path.endswith('.toml'):
                agent = tomllib.loads(text)
                self.assertEqual(Path(path).stem, agent['name'])
                self.assertIn('AGENTS.md', agent['developer_instructions'])
                self.assertNotIn('model', agent)
        self.assertIn('concurrently through `spawn_agent`', self.files['skills/dreamers-review/SKILL.md'])
        self.assertIn('`agent_type: echo`, then wait', self.files['skills/dreamers-docs/SKILL.md'])
        self.assertIn('reference it from `AGENTS.md`', self.files['dreamers/refs/project-bootstrap.md'])
        self.assertIn('Implement and review loop', self.files['skills/dreamers/SKILL.md'])
        self.assertIn('Do NOT call update_plan.', self.files['dreamers/refs/dreamers-kernel.md'])

    def test_unknown_runtime_and_adapter_drift_fail_before_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            checkout = Path(tmp) / 'checkout'
            shutil.copytree(ROOT / '.github', checkout / '.github')
            shutil.copytree(ROOT / 'adapters', checkout / 'adapters')
            skill = checkout / '.github/skills/dreamers-review/SKILL.md'
            original = skill.read_text(encoding='utf-8')
            skill.write_text(original.replace("runtime's batched-spawn mechanism", 'changed runtime'), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'adapter drift'):
                builder.package(checkout)
            skill.write_text(original + '\nUse task(unknown).\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Unconverted'):
                builder.package(checkout)

    def test_failed_generation_preserves_install_home_and_cleans_temp(self):
        shells = []
        if os.name != 'nt' and shutil.which('bash'):
            shells.append(('sh', ['bash'], '--codex-home', '--force'))
        if shutil.which('pwsh'):
            shells.append(('ps1', ['pwsh', '-NoProfile', '-File'], '-CodexHome', '-Force'))
        for extension, launcher, home_flag, force_flag in shells:
            with self.subTest(shell=extension), tempfile.TemporaryDirectory() as tmp:
                sandbox = Path(tmp)
                checkout = sandbox / 'checkout'
                for directory in ('.github', 'adapters', 'scripts'):
                    shutil.copytree(ROOT / directory, checkout / directory)
                installer = f'Install-DreamersCodex.{extension}'
                shutil.copyfile(ROOT / installer, checkout / installer)
                skill = checkout / '.github/skills/dreamers-review/SKILL.md'
                skill.write_text(skill.read_text(encoding='utf-8') + '\nUse task(unknown).\n', encoding='utf-8')
                home = sandbox / 'home'
                for relative in LEGACY + USER_FILES + ['AGENTS.md', 'skills/dreamers-lite/SKILL.md']:
                    path = home / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(b'preserve before generation\n')
                before = {p.relative_to(home): p.read_bytes() for p in home.rglob('*') if p.is_file()}
                temporary = sandbox / 'temporary'
                temporary.mkdir()
                environment = {**os.environ, 'TMPDIR': str(temporary), 'TMP': str(temporary), 'TEMP': str(temporary)}
                result = subprocess.run([*launcher, str(checkout / installer), home_flag, str(home), force_flag],
                                        env=environment, text=True, capture_output=True)
                self.assertNotEqual(0, result.returncode)
                self.assertIn('Unconverted Copilot runtime token', result.stdout + result.stderr)
                self.assertEqual(before, {p.relative_to(home): p.read_bytes() for p in home.rglob('*') if p.is_file()})
                self.assertEqual([], list(temporary.iterdir()))

    def test_global_block_contains_every_instruction_without_frontmatter(self):
        block = self.files['AGENTS.md']
        self.assertEqual((0, len(block.encode())), global_instructions.block_span(block.encode()))
        self.assertNotIn('applyTo:', block)
        for path, text in self.files.items():
            if path.startswith('dreamers/instructions/'):
                self.assertIn(Path(path).name, block)
                body = text.split('---', 2)[2].strip()
                self.assertIn(body, block)
        with self.assertRaisesRegex(ValueError, 'global applyTo'):
            global_instructions.global_block({'dreamers/instructions/scoped.md': '---\napplyTo: "*.py"\n---\nOnly Python\n'})

    def test_managed_block_preserves_user_bytes_and_verified_backups(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / 'home'
            home.mkdir()
            agents = home / 'AGENTS.md'
            personal = b'\xef\xbb\xbf# Personal rules\r\nUnicode: \xc3\xa9; no final newline'
            agents.write_bytes(personal)
            backups = Path(tmp) / 'backups'
            block = self.files['AGENTS.md'].encode()
            backup = global_instructions.update(home, 'install', block, backup_root=backups)
            self.assertEqual(personal, backup.read_bytes())
            self.assertEqual(personal + block, agents.read_bytes())
            self.assertIsNone(global_instructions.update(home, 'install', block, force=True, backup_root=backups))
            self.assertEqual(1, len(list(backups.glob('*/AGENTS.md'))))
            suffix = b'\n# Personal instructions appended later\n'
            agents.write_bytes(agents.read_bytes() + suffix)
            new_block = block.replace(b'# Dreamers global instructions', b'# Updated Dreamers global instructions')
            global_instructions.update(home, 'install', new_block, backup_root=backups)
            self.assertEqual(personal + block + suffix, agents.read_bytes())
            global_instructions.update(home, 'install', new_block, force=True, backup_root=backups)
            self.assertEqual(personal + new_block + suffix, agents.read_bytes())
            count = len(list(backups.glob('*/AGENTS.md')))
            global_instructions.update(home, 'remove', dry_run=True, backup_root=backups)
            self.assertEqual(count, len(list(backups.glob('*/AGENTS.md'))))
            self.assertEqual(personal + new_block + suffix, agents.read_bytes())
            backup = global_instructions.update(home, 'remove', backup_root=backups)
            self.assertEqual(personal + new_block + suffix, backup.read_bytes())
            self.assertEqual(personal + suffix, agents.read_bytes())

    def test_global_block_roundtrips_every_personal_line_ending(self):
        block = self.files['AGENTS.md'].encode()
        changed = block.replace(b'# Dreamers global instructions', b'# Refreshed Dreamers global instructions')
        for personal in (b'', b'personal', b'personal\n', b'personal\r\n', b'personal\r'):
            with self.subTest(ending=personal), tempfile.TemporaryDirectory() as tmp:
                home = Path(tmp) / 'home'
                home.mkdir()
                agents = home / 'AGENTS.md'
                agents.write_bytes(personal)
                backups = Path(tmp) / 'backups'
                global_instructions.update(home, 'install', block, backup_root=backups)
                global_instructions.update(home, 'install', changed, force=True, backup_root=backups)
                self.assertEqual(personal + changed, agents.read_bytes())
                global_instructions.update(home, 'remove', backup_root=backups)
                self.assertEqual(personal, agents.read_bytes())

    def test_global_block_in_new_home_and_removal_without_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / 'new home'
            block = self.files['AGENTS.md'].encode()
            self.assertIsNone(global_instructions.update(home, 'remove'))
            self.assertFalse(home.exists())
            self.assertIsNone(global_instructions.update(home, 'install', block))
            self.assertEqual(block, (home / 'AGENTS.md').read_bytes())
            global_instructions.update(home, 'remove', backup_root=Path(tmp) / 'backups')
            self.assertEqual(b'', (home / 'AGENTS.md').read_bytes())

    def test_bad_global_markers_and_override_stop_installers_before_mutation(self):
        block = self.files['AGENTS.md'].encode()
        bad_documents = [block + block, b'personal\n' + global_instructions.BEGIN + b'\nunfinished',
                         b'personal\n' + global_instructions.END + b'\n',
                         b'\n' + global_instructions.END + b'\n' + global_instructions.BEGIN + b'\n']
        for original in bad_documents:
            with self.subTest(document=original[:60]), tempfile.TemporaryDirectory() as tmp:
                home = Path(tmp)
                (home / 'AGENTS.md').write_bytes(original)
                with self.assertRaises(ValueError):
                    global_instructions.update(home, 'install', block, force=True)
                with self.assertRaises(ValueError):
                    global_instructions.update(home, 'remove')
                self.assertEqual(original, (home / 'AGENTS.md').read_bytes())
        for extension, launcher, flag in [('sh', ['bash'], '--codex-home'), ('ps1', ['pwsh', '-NoProfile', '-File'], '-CodexHome')]:
            if not shutil.which(launcher[0]) or (extension == 'sh' and os.name == 'nt'):
                continue
            for blocker in ('markers', 'override'):
                with self.subTest(shell=extension, blocker=blocker), tempfile.TemporaryDirectory() as tmp:
                    home = Path(tmp)
                    (home / 'AGENTS.md').write_bytes(b'personal\n' if blocker == 'override' else bad_documents[1])
                    if blocker == 'override':
                        (home / 'AGENTS.override.md').write_bytes(b'temporary override\n')
                    before = {p.name: p.read_bytes() for p in home.iterdir()}
                    result = subprocess.run([*launcher, str(ROOT / f'Install-DreamersCodex.{extension}'), flag, str(home)], capture_output=True)
                    self.assertNotEqual(0, result.returncode)
                    self.assertEqual(before, {p.name: p.read_bytes() for p in home.iterdir()})

    @unittest.skipIf(os.name == 'nt', 'Symlink creation on Windows requires additional permissions')
    def test_global_agents_symlink_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / 'home'
            home.mkdir()
            target = root / 'user-guidance.md'
            target.write_bytes(b'personal instructions')
            (home / 'AGENTS.md').symlink_to(target)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                global_instructions.update(home, 'install', self.files['AGENTS.md'].encode(), force=True)
            self.assertTrue((home / 'AGENTS.md').is_symlink())
            self.assertEqual(b'personal instructions', target.read_bytes())

    def test_toml_delimiters_do_not_change_prompt(self):
        prompt = "literal ''' delimiter and \\n text\nUnicode → and quotes \"\n"
        self.assertEqual(prompt, tomllib.loads(builder.agent_toml({'developer_instructions': prompt}))['developer_instructions'])

    def check_installer(self, shell):
        with tempfile.TemporaryDirectory(prefix='dreamers homes ') as tmp:
            home = Path(tmp) / 'custom codex'
            for rel in LEGACY + USER_FILES:
                path = home / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'fixture\n')
            personal = b'# Personal instructions\r\nKeep my custom guidance.\r\n'
            (home / 'AGENTS.md').write_bytes(personal)
            existing = home / 'skills/dreamers-lite/SKILL.md'
            existing.parent.mkdir(parents=True, exist_ok=True)
            existing.write_bytes(b'old skill\n')
            if shell == 'bash':
                command = ['bash', str(ROOT / 'Install-DreamersCodex.sh'), '--codex-home', str(home)]
                force = '--force'
            else:
                command = ['pwsh', '-NoProfile', '-File', str(ROOT / 'Install-DreamersCodex.ps1'), '-CodexHome', str(home)]
                force = '-Force'
            for overwrite in (False, True):
                run(*command, *([force] if overwrite else []))
                for rel, text in self.files.items():
                    if not rel.startswith(('agents/', 'skills/', 'dreamers/')):
                        continue
                    expected = b'old skill\n' if rel == 'skills/dreamers-lite/SKILL.md' and not overwrite else text.encode()
                    self.assertEqual(expected, (home / rel).read_bytes(), rel)
                self.assertEqual(personal + self.files['AGENTS.md'].encode(), (home / 'AGENTS.md').read_bytes())
                for rel in LEGACY:
                    self.assertFalse((home / rel).exists(), rel)
                for rel in USER_FILES:
                    self.assertEqual(b'fixture\n', (home / rel).read_bytes(), rel)
            if shell == 'pwsh':
                command = ['pwsh', '-NoProfile', '-File', str(ROOT / 'Remove-DreamersCodex.ps1'), '-CodexHome', str(home)]
                run(*command, '-DryRun')
                self.assertTrue(existing.exists())
                self.assertEqual(personal + self.files['AGENTS.md'].encode(), (home / 'AGENTS.md').read_bytes())
                run(*command)
                self.assertEqual(personal, (home / 'AGENTS.md').read_bytes())
                for rel in self.files:
                    if rel.startswith(('agents/', 'skills/', 'dreamers/')):
                        self.assertFalse((home / rel).exists(), rel)
                for rel in USER_FILES:
                    self.assertEqual(b'fixture\n', (home / rel).read_bytes(), rel)

    @unittest.skipUnless(os.name != 'nt' and shutil.which('bash'), 'Bash test requires a Unix shell')
    def test_bash_installer(self):
        self.check_installer('bash')

    @unittest.skipUnless(shutil.which('pwsh'), 'PowerShell is unavailable')
    def test_powershell_installer_and_removal(self):
        self.check_installer('pwsh')

    @unittest.skipUnless(os.name != 'nt' and shutil.which('bash'), 'Bash test requires a Unix shell')
    def test_codex_home_environment_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            run('bash', str(ROOT / 'Install-DreamersCodex.sh'), env={**os.environ, 'CODEX_HOME': tmp})
            self.assertEqual(self.files['agents/vigil.toml'].encode(), (Path(tmp) / 'agents/vigil.toml').read_bytes())


if __name__ == '__main__':
    unittest.main(verbosity=2)
