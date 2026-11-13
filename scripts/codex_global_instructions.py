"""Manage Dreamers' global Codex instructions without replacing user guidance."""

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import re
import shutil
import tempfile

BEGIN = b'<!-- BEGIN DREAMERS GLOBAL INSTRUCTIONS -->'
END = b'<!-- END DREAMERS GLOBAL INSTRUCTIONS -->'
BACKUPS = Path(__file__).resolve().parent.parent / '.dreamers/backups/codex-instructions'


def block_span(data):
    starts, ends = data.count(BEGIN), data.count(END)
    if starts == ends == 0:
        return None
    if starts != 1 or ends != 1:
        raise ValueError('Malformed or duplicate Dreamers global instruction markers in AGENTS.md; no files changed.')
    start, end = data.index(BEGIN), data.index(END)
    if start == 0 or data[start - 1:start] != b'\n' or end < start:
        raise ValueError('Malformed Dreamers global instruction block in AGENTS.md; no files changed.')
    end += len(END)
    if data[end:end + 2] == b'\r\n':
        end += 2
    elif data[end:end + 1] == b'\n':
        end += 1
    else:
        raise ValueError('Dreamers global instruction end marker must be on its own line.')
    if not data[start + len(BEGIN):].startswith((b'\n', b'\r\n')) or data[data.index(END) - 1:data.index(END)] != b'\n':
        raise ValueError('Dreamers global instruction start marker must be on its own line.')
    # The block owns its leading separator, allowing exact restoration of files without a final newline.
    start -= 1
    return start, end


def global_block(files):
    sections = []
    for path, text in sorted(files.items()):
        if not path.startswith('dreamers/instructions/'):
            continue
        match = re.match(r'\A---\napplyTo:\s*[\"\']\*\*[\"\']\n---\n', text)
        if not match:
            raise ValueError(f'Expected global applyTo: "**" instructions in {path}')
        sections.append(f'## {Path(path).name}\n\n{text[match.end():].strip()}')
    if not sections:
        raise ValueError('No global Codex instructions were generated')
    text = '\n' + BEGIN.decode() + '\n\n# Dreamers global instructions\n\nResolve `dreamers/` resources relative to this Codex home (`$CODEX_HOME`, default `~/.codex`).\n\n' + '\n\n'.join(sections) + '\n\n' + END.decode() + '\n'
    block_span(text.encode('utf-8'))
    return text


def read_agents(home, installing):
    agents = home / 'AGENTS.md'
    if agents.is_symlink():
        raise ValueError('AGENTS.md is a symlink; refusing to replace its target or link.')
    if agents.exists() and not agents.is_file():
        raise ValueError('AGENTS.md must be a regular file.')
    override = home / 'AGENTS.override.md'
    if installing and override.exists() and override.read_bytes().strip():
        raise ValueError('AGENTS.override.md takes precedence over AGENTS.md. Reconcile the override before installing global Dreamers instructions.')
    original = agents.read_bytes() if agents.exists() else b''
    return agents, original, block_span(original)


def update(home, action, block=None, force=False, dry_run=False, backup_root=BACKUPS):
    installing = action in ('check', 'install')
    agents, original, span = read_agents(home, installing)
    if action.startswith('check'):
        return None
    if action == 'remove':
        if span is None:
            return None
        updated = original[:span[0]] + original[span[1]:]
    else:
        if block is None or block_span(block) != (0, len(block)):
            raise ValueError('Generated AGENTS.md must contain exactly the Dreamers managed block.')
        if span and not force:
            print('SKIP global Dreamers block (exists); use --force to refresh.')
            return None
        updated = original[:span[0]] + block + original[span[1]:] if span else original + block
    if updated == original:
        return None
    if dry_run:
        print(f'WOULD UPDATE managed Dreamers block: {agents}')
        return None
    backup = None
    if agents.exists():
        stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-')
        backup_root.mkdir(parents=True, exist_ok=True)
        directory = Path(tempfile.mkdtemp(prefix=stamp, dir=backup_root))
        backup = directory / 'AGENTS.md'
        shutil.copy2(agents, backup)
        if backup.read_bytes() != original:
            raise OSError(f'AGENTS.md backup verification failed: {backup}')
        print(f'AGENTS.md backup: {backup}')
    home.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=home, prefix='.dreamers-agents-', delete=False) as output:
            temporary = Path(output.name)
            output.write(updated)
        if agents.exists():
            os.chmod(temporary, agents.stat().st_mode & 0o777)
        current = agents.read_bytes() if agents.exists() else b''
        if current != original:
            raise OSError(f'AGENTS.md changed during the update; preserved the newer file: {agents}')
        os.replace(temporary, agents)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    if agents.read_bytes() != updated:
        raise OSError(f'AGENTS.md verification failed: {agents}')
    print(f'Updated managed Dreamers block: {agents}')
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('check', 'check-remove', 'install', 'remove'))
    parser.add_argument('--codex-home', type=Path, required=True)
    parser.add_argument('--package-root', type=Path)
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    block = None
    if args.action == 'install':
        if args.package_root is None:
            parser.error('--package-root is required for installation')
        block = (args.package_root / 'AGENTS.md').read_bytes()
    update(args.codex_home, args.action, block, args.force, args.dry_run)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit(str(error)) from None
