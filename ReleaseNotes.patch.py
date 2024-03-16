import github3
import getpass
import datetime
import pytz
import time

# this is the milestone to generate the release notes for.
# it should be closed in github
LAST_RELEASE = '2023_09_4'
RELEASE = '2023_09_5'
LAST_RELEASE_DATE = datetime.datetime(2024, 1, 5, tzinfo=pytz.timezone('UTC'))

token = id = ''
with open('.git_tokens', 'r') as fd:
    token = fd.readline().strip()  # Can't hurt to be paranoid
    id = fd.readline().strip()

gh = github3.login(token=token)

repo = gh.repository('rdkit', 'rdkit')

ms = None
for m in repo.milestones(state='closed'):
    if m.title == RELEASE:
        ms = m.number
if ms is None:
    raise ValueError(f'closed milestone "{RELEASE}" not found')
# note that this apparently gets PRs too
ci = [i for i in repo.issues(state='closed', milestone=ms)]
pri = repo.pull_requests(state='closed', sort='updated', direction='desc')
prs = []
for pr in pri:
    if pr.closed_at <= LAST_RELEASE_DATE:
        break
    prs.append(pr)
#ci += prs
seen = set()
contributors = set()

relevant = [
    i for i in ci if i.milestone is not None
    and str(i.milestone) > LAST_RELEASE and i.closed_at > LAST_RELEASE_DATE
]
bugs = []
feats = []
cleanups = []
for i in relevant:
    ls = [x.name for x in i.labels()]
    if 'not in release notes' in ls:
        continue
    if 'bug' in ls:
        bugs.append(i)
    elif 'enhancement' in ls:
        feats.append(i)
    elif 'Cleanup' in ls:
        cleanups.append(i)

print("## Bug Fixes:")
#bugs = [i for i in relevant if 'bug' in (x.name for x in i.labels())]
bugs.sort(key=lambda x: x.number)
for i, bug in enumerate(bugs):
    if bug.pull_request_urls is not None:
        skipIt = any(label for label in bug.labels()
                     if 'not in release notes' in label.name)
        if not skipIt and 'merged' in [x.event for x in bug.events()]:
            text = 'pull'
        else:
            continue
    else:
        text = 'issue'
    print("  - %s\n (github %s #%d from %s)" %
          (bug.title, text, bug.number, bug.user))
    seen.add(bug.number)
    contributors.add(bug.user)

print("\n\n-----------------------------\n\n")
print("## Cleanup work:")
cleanups.sort(key=lambda x: x.number)
for i, bug in enumerate(cleanups):
    if bug.pull_request_urls is not None:
        skipIt = any(label for label in bug.labels()
                     if 'not in release notes' in label.name)
        if not skipIt and 'merged' in [x.event for x in bug.events()]:
            text = 'pull'
        else:
            continue
    else:
        text = 'issue'
    print("  - %s\n (github %s #%d from %s)" %
          (bug.title, text, bug.number, bug.user))
    seen.add(bug.number)
    contributors.add(bug.user)

print("\n\n-----------------------------\n\n")
print("## New Features and Enhancements:")
#feats = [i for i in relevant if 'enhancement' in (x.name for x in i.labels())]
feats.sort(key=lambda x: x.number)
for i, bug in enumerate(feats):
    if bug.pull_request_urls is not None:
        skipIt = any(label for label in bug.labels()
                     if 'not in release notes' in label.name)
        if not skipIt and 'merged' in [x.event for x in bug.events()]:
            text = 'pull'
        else:
            continue
    else:
        text = 'issue'
    print("  - %s\n (github %s #%d from %s)" %
          (bug.title, text, bug.number, bug.user))
    seen.add(bug.number)
    contributors.add(bug.user)

print("\n\n-----------------------------\n\n")
print("Other pull requests:")
pulls = [
    i for i in prs if str(i.milestone) in (
        ms, '', 'None') and i.merged_at and i.merged_at >= LAST_RELEASE_DATE
]
pulls.sort(key=lambda x: x.number)
for i, bug in enumerate(pulls):
    contributors.add(bug.user)
    skipIt = any(label for label in bug.labels
                 if 'not in release notes' in label.name)
    if bug.number in seen:
        skipIt = True
    if skipIt:
        continue
    print("  - %s\n (github pull #%d from %s)" %
          (bug.title, bug.number, bug.user))

print("\n\n-----------------------------\n\n")
print("All contributors:", sorted([str(x) for x in contributors]))

print("\n\n-----------------------------\nResolving names\n")
nms = []
tracking = {}
for cnm in contributors:
    u = gh.user(cnm)
    if u.name:
        nm = u.name
    else:
        nm = cnm
    nms.append(nm)
    tracking[cnm] = nm
    time.sleep(0.2)
print(tracking)
print(','.join([str(x) for x in nms]))
