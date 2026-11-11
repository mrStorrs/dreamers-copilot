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
USER_FILES = ['config.toml', 'AGENTS.md', 'skills/personal/SKILL.md', 'agents/personal.toml',
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
                for relative in LEGACY + USER_FILES + ['skills/dreamers-lite/SKILL.md']:
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
                for rel in LEGACY:
                    self.assertFalse((home / rel).exists(), rel)
                for rel in USER_FILES:
                    self.assertEqual(b'fixture\n', (home / rel).read_bytes(), rel)
            if shell == 'pwsh':
                command = ['pwsh', '-NoProfile', '-File', str(ROOT / 'Remove-DreamersCodex.ps1'), '-CodexHome', str(home)]
                run(*command, '-DryRun')
                self.assertTrue(existing.exists())
                run(*command)
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
