import hashlib
import json
from common import csv_text, encoded, instant, rows, table, text, unique
from snapshot import context, inventory


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def assess(request, ctx, receipts):
    rid = text(request.get('id'))
    key = text(request.get('providerId')), text(request.get('workId'))
    action_id = text(request.get('actionId'))
    revision = text(request.get('expectedRevision'))
    source = text(request.get('recordSource'))
    payload = request.get('input')
    if not isinstance(payload, dict) or len(json.dumps(payload, allow_nan=False)) > 16000:
        raise ValueError('Bounded supplied-record input required')
    result = {'requestId':rid, 'providerId':key[0], 'workId':key[1], 'actionId':action_id,
              'recordSource':source, 'expectedRevision':revision, 'inputSha256':digest(payload),
              'dispatchAllowed':False}
    item = ctx['items'].get(key)
    state, reason = 'unmatched_target', 'Record target is absent or outside selected observation scope'
    if item:
        prior = [r for r in receipts if r['requestId'] == rid]
        if prior:
            matching = all(r['providerId'] == key[0] and r['actionId'] == action_id for r in prior)
            statuses = {r['status'] for r in prior}
            if not matching or len(statuses) != 1:
                state, reason = 'reconcile', 'Conflicting supplied receipt identity or status'
            else:
                status = next(iter(statuses))
                state = 'recorded_complete' if status == 'completed' else 'reconcile'
                reason = 'Supplied receipt reports ' + status + '; this is not independent verification'
        elif not ctx['fresh'] or ctx['providers'][key[0]]['health'] != 'healthy' or item['health'] != 'healthy':
            state, reason = 'needs_evidence', 'Current observation is stale or unhealthy'
        elif revision != item['revision']:
            state, reason = 'needs_evidence', 'Supplied record refers to a different work revision'
        else:
            state, reason = 'record_review', 'Supplied record matched to observation; no action is available or executed'
    result.update(state=state, reason=reason)
    return result


def workflow(data):
    ctx = context(data)
    requests = rows(data, 'requests', 100)
    unique(requests)
    receipts = rows(data, 'receipts', 1000)
    for receipt in receipts:
        for field in ('requestId', 'providerId', 'actionId', 'recordSource'):
            text(receipt.get(field))
        if receipt.get('status') not in {'accepted', 'completed', 'rejected', 'failed', 'conflict', 'unknown'}:
            raise ValueError('Explicit supplied outcome required')
        if instant(receipt.get('recordedAt')) > ctx['now']:
            raise ValueError('Future receipt cannot establish an outcome')
    reviews = [assess(r, ctx, receipts) for r in requests]
    report = {'schemaVersion':1, 'snapshotId':ctx['id'], 'scope':ctx['scope'], 'fresh':ctx['fresh'],
              'missingProviders':ctx['gaps'], 'unhealthyProviders':ctx['unhealthy'], 'actions':reviews,
              'evidence':'User-supplied records only; authenticity and outcomes not independently verified',
              'dispatchAllowed':False, 'observations':inventory(ctx), 'recordCount':len(reviews),
              'execution':'Miilo observes coding agents locally, read-only, with no control actions. '
                          'Miilo Control only reviews supplied action records and never runs them.'}
    alias_note = 'Unassigned source work was explicitly given a local review label; this is not source workspace membership.'
    if isinstance(data.get('exportMetadata'), dict) and data['exportMetadata'].get('unassignedWorkspaceLabel'):
        report['workspaceNote'] = alias_note
    fields = ['requestId', 'providerId', 'workId', 'actionId', 'recordSource', 'dispatchAllowed', 'state', 'reason']
    rendered = [{**row, 'dispatchAllowed':'false'} for row in reviews]
    brief = '# Miilo Control\n\n' + report['execution'] + '\n\ndispatchAllowed=false\n'
    brief += '\n## Observed work\n\n' + table(['providerId','workId','workspaceId','title','summary','lifecycle','attention','health'], inventory(ctx))
    brief += '\n## Supplied action records\n\n' + table(fields, rendered)
    if not reviews:
        brief += '\nNo action records supplied. This is an observation review only; no action outcomes can be inferred.\n'
    if 'workspaceNote' in report:
        brief += '\n' + alias_note + '\n'
    brief += '\nFresh snapshot: ' + str(ctx['fresh']) + '\nMissing providers: ' + str(len(ctx['gaps']))
    brief += '; unhealthy providers: ' + str(len(ctx['unhealthy']))
    brief += '\n\nReview source records manually; a matched record is not permission or evidence of execution.\n'
    return {'review.json':encoded(report), 'action-review.csv':csv_text(fields, rendered), 'review.md':brief,
            'work.csv':csv_text(list(inventory(ctx)[0]) if ctx['items'] else ['providerId','workId'], inventory(ctx))}
