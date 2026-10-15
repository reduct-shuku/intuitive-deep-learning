#!/usr/bin/env python3
"""Validate a Shuku repository without executing any course code."""
from pathlib import Path, PurePosixPath
import argparse
import json
import re


def validate(root):
    root = Path(root).resolve()
    errors = []
    def need(ok, message):
        if not ok:
            errors.append(message)
    def local_file(path):
        if not isinstance(path, str) or not path or len(path) >= 240 or re.search(r'[\\\x00-\x1f\x7f?#%:]', path):
            return False
        if any(p in ('', '.', '..') for p in path.split('/')):
            return False
        target = root / path
        return target.is_file() and not target.is_symlink() and target.resolve().is_relative_to(root)
    for name in ('README.md', 'SKILL.md', 'shuku.json', 'CONTRIBUTING.md'):
        need(local_file(name), f'Missing required ordinary file: {name}')
    need(not (root / 'course.yaml').exists(), 'Remove course.yaml after migrating its fields into shuku.json')
    if errors:
        return errors
    try:
        data = json.loads((root / 'shuku.json').read_text(encoding='utf-8'))
        need(isinstance(data, dict), 'shuku.json must be an object')
        if not isinstance(data, dict):
            return errors
        template = (root / '.template').is_file()
        for key in ('schema_version','name','title','description','version','repository','entry','type','build_profile'):
            need(key in data, f'Missing field: {key}')
        need(type(data.get('schema_version')) is int and data['schema_version'] == 1, 'schema_version must be 1')
        need(data.get('type') == 'official', 'type must be official')
        need(data.get('build_profile') in ('static','skill'), 'build_profile must be static or skill')
        need(isinstance(data.get('version'), str) and re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', data['version']), 'version must use three numeric components')
        for key, limit in (('title',160),('description',5000)):
            need(isinstance(data.get(key), str) and bool(data[key].strip()) and len(data[key]) <= limit, f'Invalid {key}')
        path = data.get('path', '.')
        need(isinstance(path, str) and (path == '.' or (path and not re.search(r'[\\\x00-\x1f?#%:]',path) and all(p not in ('','.','..') for p in path.split('/')))), 'Invalid path')
        entry = data.get('entry')
        if isinstance(path, str) and isinstance(entry, str):
            need(local_file(entry if path == '.' else path + '/' + entry), 'Content entry does not exist or is unsafe')
        else:
            need(False, 'Invalid entry')
        if data.get('build_profile') == 'static':
            need(isinstance(entry,str) and entry.endswith('.html'), 'Static entry must be HTML')
        if 'course_id' in data:
            need(isinstance(data['course_id'],str) and re.fullmatch(r'[\w-]{1,128}',data['course_id'],re.ASCII), 'Invalid course_id')
        if 'ref' in data:
            need(isinstance(data['ref'],str) and 0 < len(data['ref']) <= 255 and data['ref'].strip() == data['ref'] and not re.search(r'[\x00-\x1f\x7f]',data['ref']), 'Invalid ref')
        need(local_file(data.get('contributing','CONTRIBUTING.md')), 'Contribution guide does not exist')
        if 'changes' in data:
            need(isinstance(data['changes'],list) and len(data['changes']) <= 100 and all(isinstance(x,str) and len(x) <= 2000 for x in data['changes']), 'Invalid changes')
        skill = (root / 'SKILL.md').read_text(encoding='utf-8')
        front = re.match(r'\A---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)',skill)
        need(front is not None, 'SKILL.md requires YAML frontmatter')
        if front:
            name = re.search(r'^name:\s*(.+)$',front[1],re.M)
            desc = re.search(r'^description:\s*(.+)$',front[1],re.M)
            need(name is not None and name[1].strip() == data.get('name'), 'Skill name must match shuku.json')
            need(desc is not None and bool(desc[1].strip()), 'Skill description is required')
        if not template:
            need(isinstance(data.get('name'),str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',data['name']) and len(data['name']) <= 100, 'Invalid name')
            need(isinstance(data.get('repository'),str) and re.fullmatch(r'https://github\.com/[\w.-]+/[\w.-]+',data['repository']) and not data['repository'].endswith('.git'), 'Invalid repository')
            for name in ('README.md','SKILL.md','shuku.json','CONTRIBUTING.md'):
                need(not re.search(r'\{\{[A-Z0-9_]+\}\}',(root/name).read_text(encoding='utf-8')), f'Unresolved placeholders: {name}')
    except (ValueError, OSError, TypeError) as error:
        errors.append(f'Invalid course files: {error}')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', default=Path(__file__).resolve().parents[1])
    errors = validate(parser.parse_args().root)
    for error in errors:
        print('[ERROR] ' + error)
    if not errors:
        print('[OK] Shuku course files are valid.')
    raise SystemExit(bool(errors))
