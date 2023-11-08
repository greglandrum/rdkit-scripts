import github3
import getpass
import datetime
import pytz
import time

# this is the milestone to generate the release notes for.
# it should be closed in github
RELEASE = '2023_03_3'
LAST_RELEASE_DATE = datetime.datetime(2023, 6, 19, tzinfo=pytz.timezone('UTC'))

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
bugs = ci

prs = []

print("## Bug Fixes:")
bugs.sort(key=lambda x: x.number)
contributors = set()
seen = set()

for i, bug in enumerate(bugs):
  skipIt = any(label for label in bug.labels() if 'not in release notes' in label.name)
  if not skipIt:
    print(f"  - {bug.title}\n (github #{bug.number} from {bug.user})")
  contributors.add(bug.user)
  seen.add(bug.number)

pri = repo.pull_requests(state='closed', sort='updated', direction='desc')
prs = []
for pr in pri:
  if pr.closed_at <= LAST_RELEASE_DATE:
    break
  prs.append(pr)

print("Other pull requests:")
pulls = [
  i for i in prs
  if str(i.milestone) in (ms, '', 'None') and i.merged_at and i.merged_at >= LAST_RELEASE_DATE
]
pulls.sort(key=lambda x: x.number)
for i, bug in enumerate(pulls):
  contributors.add(bug.user)
  skipIt = any(label for label in bug.labels if 'not in release notes' in label['name'])
  if bug.number in seen:
    skipIt = True
  if skipIt:
    continue
  print("  - %s\n (github pull #%d from %s)" % (bug.title, bug.number, bug.user))

print("\n\n-----------------------------\n\n")
print("All contributors:", sorted([str(x) for x in contributors]))

print("\n\n-----------------------------\nResolving names\n")
nms = []
for nm in contributors:
  u = gh.user(nm)
  if u.name:
    nms.append(u.name)
  else:
    nms.append(str(nm))
  time.sleep(0.2)
print(', \n'.join(nms))
