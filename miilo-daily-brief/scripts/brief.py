from common import csv_text, encoded, instant, table
from snapshot import context, inventory


def workflow(data):
    current = context(data)
    since = instant(data.get('since'))
    if since > current['now']:
        raise ValueError('Brief window cannot begin in the future')
    previous = context(data, previous=True) if data.get('previousSnapshot') is not None else None
    if previous and (previous['observed'] >= current['observed'] or previous['observed'] > since):
        raise ValueError('Baseline must precede snapshot and be at or before window start')
    changes, attention, counts = [], [], {}
    for key, item in sorted(current['items'].items()):
        counts[item['lifecycle']] = counts.get(item['lifecycle'], 0) + 1
        if item['attention'] not in {'none', 'informational'} or item['lifecycle'] in {'waiting', 'failed'} or item['health'] != 'healthy':
            attention.append({'providerId':key[0], 'workId':key[1], 'title':item['title'],
                              'attention':item['attention'], 'health':item['health'], 'lifecycle':item['lifecycle']})
        old = previous['items'].get(key) if previous else None
        if old is None:
            change = 'first_observed' if previous else 'baseline_unavailable'
        elif any(item[field] != old[field] for field in ('revision','lifecycle','attention','health','summary','title')):
            change = 'changed_between_snapshots'
        else:
            continue
        changes.append({'providerId':key[0], 'workId':key[1], 'title':item['title'], 'change':change,
                        'lifecycle':item['lifecycle'], 'updatedAt':item['updatedAt'],
                        'updatedWithinWindow':since <= instant(item['updatedAt']) <= current['now']})
    if previous:
        for key, old in sorted(previous['items'].items()):
            if key not in current['items']:
                changes.append({'providerId':key[0], 'workId':key[1], 'title':old['title'],
                                'change':'not_observed_now', 'lifecycle':'unknown', 'updatedAt':old['updatedAt'],
                                'updatedWithinWindow':False})
    report = {'schemaVersion':1, 'snapshotId':current['id'], 'scope':current['scope'], 'fresh':current['fresh'],
              'baselineSnapshotId':previous['id'] if previous else None, 'since':data['since'],
              'missingProviders':current['gaps'], 'unhealthyProviders':current['unhealthy'],
              'observedCounts':counts, 'changes':changes, 'needsYou':attention,
              'limits':['Supplied observations only; no independently verified runtime outcomes.',
                        'Between-snapshot changes are not an exhaustive event history.',
                        'Not observed now does not mean deleted, completed or disconnected.',
                        'Reported complete is not proof that tests, deployment or publication succeeded.',
                        'No scheduler, delivery, live monitoring or external actions were executed.']}
    if isinstance(data.get('exportMetadata'), dict) and data['exportMetadata'].get('unassignedWorkspaceLabel'):
        report['limits'].append('Unassigned source work has an explicit local review label, not source workspace membership.')
    md = '# Miilo Daily Brief\n\nFresh snapshot: ' + str(current['fresh'])
    md += '\n\nMissing providers: ' + str(len(current['gaps'])) + '; unhealthy providers: ' + str(len(current['unhealthy']))
    md += '\n\n## Needs you\n\n' + table(['providerId','workId','title','attention','health','lifecycle'], attention)
    md += '\n## Changes\n\n' + table(['providerId','workId','title','change','lifecycle','updatedWithinWindow'], changes)
    md += '\n## Limits\n\n' + '\n'.join('- ' + s for s in report['limits']) + '\n'
    return {'brief.json':encoded(report), 'brief.md':md,
            'changes.csv':csv_text(['providerId','workId','title','change','lifecycle','updatedAt','updatedWithinWindow'], changes),
            'needs-you.csv':csv_text(['providerId','workId','title','attention','health','lifecycle'], attention),
            'work.csv':csv_text(list(inventory(current)[0]) if current['items'] else ['providerId','workId'], inventory(current))}
