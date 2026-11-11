#!/usr/bin/env python3
"""Build the Codex package from the catalog-backed Copilot source tree."""

import argparse
import json
from pathlib import Path
import re
import sys
try:
    import tomllib
except ModuleNotFoundError:
    sys.exit('Python 3.11 or newer is required to build Dreamers Codex.')

ROOT = Path(__file__).resolve().parent.parent
PREAMBLE = """## Codex runtime
Read `../../dreamers/refs/codex-runtime.md` relative to this skill directory for resource resolution, progress tracking, user gates, and delegation. Use the user's message as skill input, including paths and flags.
Before executing this skill, read `../../dreamers/instructions/dreamers.instructions.md` and `../../dreamers/instructions/dreamers.laws.md`. Codex does not auto-load these compatibility instruction files.
"""
INLINE = re.compile(r"^<([\w-]+)>\n.*?^</\1>", re.MULTILINE | re.DOTALL)


def frontmatter(text):
    if not text.startswith('---\n'):
        raise ValueError('Missing YAML frontmatter')
    header, body = text[4:].split('\n---\n', 1)
    fields = {}
    for line in header.splitlines():
        key, value = line.split(':', 1)
        value = value.strip()
        if value.startswith('"'):
            value = json.loads(value)
        elif value.startswith("'"):
            value = value[1:-1].replace("''", "'")
        fields[key] = value
    if not re.fullmatch(r'[a-z][a-z0-9-]*', fields.get('name', '')) or not fields.get('description'):
        raise ValueError('Frontmatter needs name and description')
    return fields, body


def translate(text):
    text = re.sub(r'`\.github/copilot-instructions\.md`(?: \(project-level, if present\)| if present| when present)?',
                  '`AGENTS.md`, `CODEX.md`, or `PROJECT_INSTRUCTIONS_COMPAT` when present', text)
    replacements = [
        ('`~/.copilot/copilot-instructions.md`', '`Codex global instructions, if configured`'),
        ('~/.copilot/dreamers/', 'dreamers/'),
        ('.github/dreamers/', 'dreamers/'),
        ('.github/skills/', 'skills/'),
        ('.github/agents/', 'agents/'),
        ('.agent.md', '.toml'),
        ('manage_todo_list', 'update_plan'),
        ('Call `request_information`', 'Ask the user'),
        ('call `request_information`', 'ask the user'),
        ('Use `request_information`', 'Ask the user'),
        ('use `request_information`', 'ask the user directly'),
        ('through `request_information`', 'by asking the user'),
        ('via `request_information`', 'by asking the user'),
        ('`request_information`', 'asking the user'),
        ('request_information', 'ask the user'),
        ('via `view`', 'by reading the local file'),
        ('$ARGUMENTS', '<skill input>'),
        ('Read, Write, Edit, Glob, Grep, Bash', 'Codex file and shell tools'),
        ('Edit / Write / Bash tools', 'file and shell tools'),
        ('own Edit / Write / Bash tools', 'own file and shell tools'),
        ('mode: sync', 'concurrent spawns, then wait'),
        ('one tool-call with 3 sub-tool-uses', 'concurrent Codex agent spawns'),
        ('Copilot CLI', 'Codex'),
        ('things Copilot must', 'things Codex must'),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    # Match command names only; paths such as ../../dreamers must retain their slash.
    text = re.sub(r'(?<![\w./-])/dreamers(?=[\s`*"<]|-|$)', 'dreamers', text)
    text = text.replace('PROJECT_INSTRUCTIONS_COMPAT', '.github/copilot-instructions.md')
    return '\n'.join(line.rstrip() for line in text.splitlines()).strip() + '\n'


def agent_toml(fields):
    lines = []
    for key, value in fields.items():
        if key == 'developer_instructions' and "'" * 3 not in value:
            encoded = "'" * 3 + "\n" + value + "'" * 3
        else:
            encoded = json.dumps(value, ensure_ascii=False)
        lines.append(f'{key} = {encoded}')
    return '\n'.join(lines) + '\n'


def package(root=ROOT):
    source = root / '.github'
    adapter = root / 'adapters/codex'
    rules = json.loads((adapter / 'replacements.json').read_text(encoding='utf-8'))
    files = {}
    for directory, target in [('dreamers/refs', 'dreamers/refs'), ('dreamers/templates', 'dreamers/templates'), ('instructions', 'dreamers/instructions'), ('skills', 'skills'), ('agents', 'agents')]:
        for path in sorted((source / directory).rglob('*.md')):
            rel = (Path(target) / path.relative_to(source / directory)).as_posix()
            if directory == 'skills' and not (path.parts[-2] == 'dreamers' or path.parts[-2].startswith('dreamers-')):
                continue
            text = path.read_text(encoding='utf-8-sig')
            text = INLINE.sub(lambda match: f'@@REF:{match[1]}@@' if (source / 'dreamers/refs' / f'{match[1]}.md').is_file() else match[0], text)
            for replacement in rules.get(rel, []):
                if text.count(replacement['from']) != 1:
                    raise ValueError(f'Codex adapter drift in {rel}: {replacement["from"]!r}')
                text = text.replace(replacement['from'], replacement['to'])
            if directory == 'skills' and path.name == 'SKILL.md':
                fields, body = frontmatter(text)
                description = translate(fields['description']).strip().replace('Triggers:', 'Use when the user asks for')
                body = re.sub(r'^\$ARGUMENTS\s*$', '', body, flags=re.MULTILINE)
                text = f'---\nname: {fields["name"]}\ndescription: {json.dumps(description, ensure_ascii=False)}\n---\n\n{PREAMBLE}\n{translate(body)}'
            elif directory == 'agents':
                fields, body = frontmatter(text)
                rel = f'agents/{fields["name"]}.toml'
                text = agent_toml({
                    'name': fields['name'], 'description': translate(fields['description']).strip(),
                    'sandbox_mode': 'workspace-write', 'developer_instructions': translate(body),
                })
            else:
                text = translate(text)
            files[rel] = text
    missing_rules = set(rules) - {p.replace('.toml', '.agent.md') for p in files}
    if missing_rules:
        raise ValueError(f'Adapter targets missing from source: {sorted(missing_rules)}')
    files['dreamers/refs/codex-runtime.md'] = (adapter / 'runtime.md').read_text(encoding='utf-8')
    refs = {Path(path).stem: text.rstrip('\n') for path, text in files.items() if path.startswith('dreamers/refs/')}
    for path, text in files.items():
        def inline(match):
            name = match[1]
            if name not in refs:
                raise ValueError(f'Unknown inline ref {name} in {path}')
            return f'<{name}>\n{refs[name]}\n</{name}>'
        if path.endswith('.toml'):
            data = tomllib.loads(text)
            data['developer_instructions'] = re.sub(r'@@REF:([\w-]+)@@', inline, data['developer_instructions'])
            files[path] = agent_toml(data)
        else:
            files[path] = re.sub(r'@@REF:([\w-]+)@@', inline, text)
    catalog = json.loads((source / 'catalog.json').read_text(encoding='utf-8'))
    for item in catalog['items']:
        if item.get('path'):
            item['path'] = item['path'].removeprefix('.github/').replace('.agent.md', '.toml')
            if item['path'].startswith('instructions/'):
                item['path'] = 'dreamers/' + item['path']
        if item.get('description'):
            item['description'] = translate(item['description']).strip()
    for collection in catalog.get('collections', []):
        collection['readmePath'] = 'README.md'
    for folder in catalog.get('folderTargets', []):
        folder['sourcePath'] = folder['sourcePath'].removeprefix('.github/')
        if folder['sourcePath'] == 'instructions':
            folder['sourcePath'] = 'dreamers/instructions'
            folder['destSubpath'] = 'dreamers/instructions'
    files['.github/catalog.json'] = json.dumps(catalog, indent=2, ensure_ascii=False) + '\n'
    files['.codex-plugin/plugin.json'] = (adapter / 'plugin.json').read_text(encoding='utf-8')
    files['README.md'] = '# Dreamers Codex\n\nGenerated from the shared Dreamers repository. Edit `.github/` sources and `adapters/codex/`, then rebuild; do not edit this output.\n'
    validate(files)
    return files


def validate(files):
    stale = re.compile(r'task\(|manage_todo_list|request_information|\$ARGUMENTS|mode:\s*[\"\']?sync|\.github/(?:agents|skills|dreamers)/|~/.copilot')
    refs = {Path(p).stem: t.rstrip('\n') for p, t in files.items() if p.startswith('dreamers/refs/')}
    for path, text in files.items():
        if path.endswith('.toml'):
            text = tomllib.loads(text)['developer_instructions']
        if path != 'dreamers/refs/codex-runtime.md' and stale.search(text):
            raise ValueError(f'Unconverted Copilot runtime token in {path}: {stale.search(text)[0]}')
        for match in INLINE.finditer(text):
            if match[1] in refs and match[0] != f'<{match[1]}>\n{refs[match[1]]}\n</{match[1]}>':
                raise ValueError(f'Inline ref drift in {path}: {match[1]}')
    catalog = json.loads(files['.github/catalog.json'])
    for item in catalog['items']:
        if item.get('path') and item['path'] not in files:
            raise ValueError(f'Catalog target missing: {item["path"]}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='Empty destination for generated package')
    args = parser.parse_args()
    files = package()
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('Output directory must be empty; choose a fresh build directory')
    for relative, text in files.items():
        path = args.output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline='\n')
    print(f'Built and validated {len(files)} Codex package files in {args.output}')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError) as error:
        sys.exit(str(error))
