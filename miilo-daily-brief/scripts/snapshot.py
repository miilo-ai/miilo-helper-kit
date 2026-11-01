from common import instant, rows, text, unique

HEALTH = {'healthy', 'delayed', 'stale', 'degraded', 'unreachable'}
LIFECYCLE = {'queued', 'active', 'waiting', 'complete', 'failed', 'cancelled'}
ATTENTION = {'none', 'informational', 'decision', 'approval', 'intervention'}


def names(value):
    if not isinstance(value, list) or not value or len(value) > 200 or any(not isinstance(x, str) for x in value):
        raise ValueError('Explicit bounded nonempty scope required')
    if len(set(value)) != len(value):
        raise ValueError('Duplicate scope identity')
    return {text(x) for x in value}


def context(data, previous=False):
    now = instant(data.get('assessmentTime'))
    age = data.get('maxAgeSeconds')
    if type(age) is not int or not 1 <= age <= 3600:
        raise ValueError('Freshness budget must be 1 to 3600 seconds')
    scope = data.get('scope')
    if not isinstance(scope, dict):
        raise ValueError('Explicit scope required')
    allowed = names(scope.get('providerIds')), names(scope.get('workspaceIds'))
    snap = data.get('previousSnapshot' if previous else 'snapshot')
    if not isinstance(snap, dict) or snap.get('protocolVersion') != '0.1':
        raise ValueError('Supported Miilo snapshot projection required')
    snapshot_id = text(snap.get('snapshotId'))
    observed = instant(snap.get('observedAt'))
    elapsed = (now - observed).total_seconds()
    if elapsed < 0:
        raise ValueError('Future snapshot cannot establish current evidence')
    providers = unique(rows(snap, 'providers'))
    for p in providers.values():
        if p.get('health') not in HEALTH or not isinstance(p.get('capabilities'), dict):
            raise ValueError('Provider health and capabilities required')
        control = p['capabilities'].get('control')
        if control != []:
            raise ValueError('Miilo local observation is read-only; control must be empty')
    items = {}
    for item in rows(snap, 'workItems'):
        key = text(item.get('providerId')), text(item.get('id'))
        if key in items or key[0] not in providers:
            raise ValueError('Duplicate work identity or unknown provider')
        for field in ('revision', 'title'):
            text(item.get(field))
        if not isinstance(item.get('summary'), str) or len(item['summary']) > 10000:
            raise ValueError('Bounded work summary required; empty means unavailable')
        if item.get('lifecycle') not in LIFECYCLE or item.get('health') not in HEALTH or item.get('attention') not in ATTENTION:
            raise ValueError('Unsupported work state')
        if instant(item.get('updatedAt')) > observed:
            raise ValueError('Work update is later than snapshot')
        if item.get('workspaceId') is not None:
            text(item['workspaceId'])
        if rows(item, 'actions'):
            raise ValueError('Miilo local observation exposes no control actions')
        items[key] = item
    selected = {k:v for k,v in items.items() if k[0] in allowed[0] and v.get('workspaceId') in allowed[1]}
    gaps = sorted(allowed[0] - providers.keys())
    unhealthy = sorted(k for k in allowed[0] & providers.keys() if providers[k]['health'] != 'healthy')
    return {'now':now, 'observed':observed, 'id':snapshot_id, 'fresh':elapsed <= age, 'providers':providers,
            'items':selected, 'gaps':gaps, 'unhealthy':unhealthy, 'scope':scope}


def inventory(ctx):
    return [{'providerId':k[0], 'workId':k[1], 'workspaceId':v['workspaceId'], 'title':v['title'],
             'summary':v['summary'], 'lifecycle':v['lifecycle'], 'health':v['health'],
             'attention':v['attention'], 'revision':v['revision'], 'updatedAt':v['updatedAt']}
            for k,v in sorted(ctx['items'].items())]
