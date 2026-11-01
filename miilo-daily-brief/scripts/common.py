import argparse
import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation, getcontext
import io
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile


getcontext().prec = 80


def text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 10000:
        raise ValueError('Nonempty bounded text required')
    return value


def rows(data, key, limit=2000):
    value = data.get(key)
    if not isinstance(value, list) or len(value) > limit or any(not isinstance(x, dict) for x in value):
        raise ValueError('Bounded object array required: ' + key)
    return value


def unique(items, key='id'):
    result = {}
    for item in items:
        name = text(item.get(key))
        if name in result:
            raise ValueError('Duplicate identity: ' + key)
        result[name] = item
    return result


def number(value):
    if isinstance(value, (bool, float)) or not isinstance(value, (str, int)):
        raise ValueError('Exact numeric strings or integers required')
    try:
        result = Decimal(value)
    except InvalidOperation as error:
        raise ValueError('Invalid decimal') from error
    if not result.is_finite() or len(str(value)) > 64 or len(result.as_tuple().digits) > 24 or abs(result.adjusted()) > 18:
        raise ValueError('Bounded finite decimal required')
    return result


def instant(value):
    parsed = datetime.fromisoformat(text(value).replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timestamp timezone required')
    return parsed


def clean(value):
    return re.sub(r'(?i)\b(password|token|api[_-]?key|secret)\s*[:=]\s*[^\s,;]+', r'\1=[REDACTED]', str(value))


def cell(value):
    return clean(value).replace('|', '\\|').replace('\r', ' ').replace('\n', ' ').replace('<', '&lt;').replace('>', '&gt;')


def csv_text(fields, records):
    output = io.StringIO(newline='')
    writer = csv.writer(output, lineterminator='\n')
    writer.writerow(fields)
    for record in records:
        values = []
        for key in fields:
            value = clean(record.get(key, ''))
            if value.lstrip().startswith(('=', '+', '-', '@')) or value.startswith(('\t', '\r', '\n')):
                value = "'" + value
            values.append(value)
        writer.writerow(values)
    return output.getvalue()


def table(fields, records):
    return '\n'.join(['| ' + ' | '.join(fields) + ' |', '| ' + ' | '.join(['---'] * len(fields)) + ' |'] +
                     ['| ' + ' | '.join(cell(row.get(key, '')) for key in fields) + ' |' for row in records]) + '\n'


def scrub(value):
    if isinstance(value,str):
        return clean(value)
    if isinstance(value,list):
        return [scrub(item) for item in value]
    if isinstance(value,dict):
        return {clean(key):scrub(item) for key,item in value.items()}
    return value


def encoded(value, redact=True):
    return json.dumps(scrub(value) if redact else value, indent=2, ensure_ascii=False) + '\n'


def write_packet(files, target):
    if target.exists() or target.is_symlink() or not target.parent.is_dir():
        raise ValueError('New output directory under existing parent required')
    stage = Path(tempfile.mkdtemp(prefix='.microproduct-', dir=target.parent))
    try:
        os.chmod(stage, 0o700)
        for name, content in files.items():
            if Path(name).name != name:
                raise ValueError('Flat output names required')
            path = stage / name
            path.write_text(content)
            os.chmod(path, 0o600)
        if target.exists() or target.is_symlink():
            raise ValueError('Output already exists')
        stage.rename(target)
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def execute(workflow):
    parser = argparse.ArgumentParser(description='Prepare a local review packet. No external writes or model calls.')
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        if args.input.stat().st_size > 1048576:
            raise ValueError('Input exceeds one MiB')
        data = json.loads(args.input.read_text())
        if not isinstance(data, dict):
            raise ValueError('Object input required')
        files = workflow(data)
        write_packet(files, args.output)
    except (OSError, ValueError, TypeError, KeyError, ArithmeticError, ImportError) as error:
        kind = 'dependency unavailable' if isinstance(error, ImportError) else 'input or output invalid'
        print('Cannot prepare packet: ' + kind + '. No input values were printed.', file=sys.stderr)
        return 2
    print(f'Prepared {len(files)} local review files. No external actions or model calls.')
    return 0
