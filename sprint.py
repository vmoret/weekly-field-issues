from functools import partial
from itertools import groupby


def calc_handled_in_active_sprint(itrack, boards=None, projects=None, 
                                  observed_during=None, severities=None):

    getitem = lambda mapping, key, *rest: getitem(mapping[key], *rest) if len(rest) != 0 else mapping[key]
    getfield = lambda mapping, *keys: getitem(mapping, 'fields', *keys)
    getvalue = lambda mapping, key: getfield(mapping, key, 'value')
    
    def validate_issue(issue, projects=projects, observed_during=observed_during):
        matches = len([x for x in projects if x in getfield(issue, 'project').values()])
        return matches != 0 and 'defect' in getfield(issue, 'issuetype', 'name') \
                and getvalue(issue, 'customfield_10021') in observed_during
    
    def process_story(story, itrack, validate):
        if validate(story):
            yield story
            raise StopIteration

        linked = (links[direction] for direction in ('outwardIssue', 'inwardIssue')
                  for links in getfield(story, 'issuelinks') if direction in links)
        issues = (itrack.issue(x) for x in set(link['self'] for link in linked))
        yield from (issue for issue in issues if validate(issue))

    sprints = set(y for x in boards for y in itrack.sprints(x))
    stories = (y for x in sprints for y in itrack.stories(x))
    issues = (y for x in stories for y in process_story(x, itrack, validate_issue))
    counts = {k: len(list(v)) for k, v in groupby(sorted(getvalue(x, 'customfield_10002') for x in issues))}
    return [counts[k] if k in counts else 0 for k in severities]

