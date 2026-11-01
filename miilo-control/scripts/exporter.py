import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import tempfile
from common import encoded, text, write_packet
from snapshot import context

LIMIT = 1048576
WORK_FIELDS = ('id','providerId','workspaceId','title','summary','revision','updatedAt','lifecycle','health','attention','actions')


def read_json(path):
    if path.stat().st_size > LIMIT:
        raise ValueError('Input too large')
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError('JSON object required')
    return value


def capture_local():
    with tempfile.TemporaryFile() as output:
        result = subprocess.run(['miilo','local','snapshot'], stdout=output, stderr=subprocess.DEVNULL, timeout=15)
        output.seek(0)
        raw = output.read(LIMIT + 1)
    if result.returncode or len(raw) > LIMIT:
        raise ValueError('Local snapshot unavailable')
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError('Snapshot object required')
    return value


def project(source, providers, workspaces, unassigned):
    selected_providers = [dict(id=p['id'], health=p['health'], capabilities={'control':p['capabilities']['control']})
                          for p in source['providers'] if p['id'] in providers]
    items = []
    for item in source['workItems']:
        if item['providerId'] not in providers:
            continue
        workspace = item.get('workspaceId')
        if workspace is None and unassigned:
            workspace = unassigned
        if workspace not in workspaces:
            continue
        record = {k:item[k] for k in WORK_FIELDS if k != 'workspaceId'}
        record['workspaceId'] = workspace
        if item.get('workspaceId') is None:
            record['sourceWorkspaceId'] = None
        items.append(record)
    return {'protocolVersion':source['protocolVersion'], 'snapshotId':source['snapshotId'],
            'observedAt':source['observedAt'], 'providers':selected_providers, 'workItems':items}


def envelope(source, args, mode):
    providers, workspaces = list(dict.fromkeys(args.provider_id)), list(dict.fromkeys(args.workspace_id))
    if not providers or not workspaces or (args.unassigned_workspace and args.unassigned_workspace not in workspaces):
        raise ValueError('Explicit providers/workspaces and matching unassigned label required')
    data = {'assessmentTime':args.assessment_time or datetime.now(timezone.utc).isoformat(),
            'maxAgeSeconds':args.max_age_seconds, 'scope':{'providerIds':providers, 'workspaceIds':workspaces},
            'snapshot':project(source, providers, workspaces, args.unassigned_workspace),
            'exportMetadata':{'unassignedWorkspaceLabel':args.unassigned_workspace,
                              'scope':'Local projection only; not a Miilo workspace assignment or network upload'}}
    if mode == 'brief':
        data['since'] = text(args.since)
        if args.previous_snapshot:
            data['previousSnapshot'] = project(read_json(args.previous_snapshot), providers, workspaces, args.unassigned_workspace)
    else:
        records = read_json(args.records) if args.records else {'requests':[], 'receipts':[]}
        data.update(requests=records['requests'], receipts=records['receipts'])
    context(data)
    return data


def main(mode):
    parser = argparse.ArgumentParser(description='Prepare a scoped local Miilo review input. Never uploads or controls agents.')
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--snapshot', type=Path)
    source.add_argument('--capture-local', action='store_true', help='Read the existing selection using miilo local snapshot once')
    parser.add_argument('--list', action='store_true', help='Print provider/workspace IDs only, without titles or summaries')
    parser.add_argument('--provider-id', action='append', default=[])
    parser.add_argument('--workspace-id', action='append', default=[])
    parser.add_argument('--unassigned-workspace', help='Explicit local review label for null workspace IDs, not source membership')
    parser.add_argument('--assessment-time')
    parser.add_argument('--max-age-seconds', type=int, default=60)
    parser.add_argument('--since')
    parser.add_argument('--previous-snapshot', type=Path)
    parser.add_argument('--records', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        value = capture_local() if args.capture_local else read_json(args.snapshot)
        if args.list:
            print(json.dumps({'providerIds':[p['id'] for p in value['providers']],
                              'workspaceIds':sorted({w['workspaceId'] for w in value['workItems'] if w.get('workspaceId') is not None}),
                              'hasUnassignedWork':any(w.get('workspaceId') is None for w in value['workItems'])}))
        else:
            if not args.output:
                raise ValueError('New output directory required')
            data = envelope(value, args, mode)
            output = encoded(data)
            if len(output.encode()) > LIMIT:
                raise ValueError('Combined review input too large')
            write_packet({'input.json':output}, args.output)
            print('Scoped input.json prepared locally. Review it before sharing. No upload or agent actions.')
    except (OSError, ValueError, TypeError, KeyError, AttributeError, subprocess.SubprocessError):
        print('Export unavailable: check source, selection, timestamps and output directory. For capture, check miilo local doctor; no collector was started.')
        return 2
    return 0
