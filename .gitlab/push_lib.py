#!/usr/bin/env python3
"""push_lib.py — GitLab API logic behind push_to_gitlab.sh (stdlib only).

Reads configuration from environment variables set by the shell wrapper.
Never prints the token; every failing API call is reported with the HTTP
status and the server message instead.
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# ═════════════════════════════════════════════════════════════════════════════
# Configuration from the wrapper
HOST = os.environ.get('GITLAB_HOST', 'https://gitlab.com').rstrip('/')
PROJECT_ID = os.environ.get('PROJECT_ID', '89425673')
DEFAULT_BRANCH = os.environ.get('DEFAULT_BRANCH', 'main')
TARGET_BRANCH = os.environ.get('TARGET_BRANCH', 'main')
OPEN_MR = os.environ.get('OPEN_MR') == 'true'
DRY_RUN = os.environ.get('DRY_RUN') == 'true'
SKIP_PUSH = os.environ.get('SKIP_PUSH') == 'true'
SKIP_CONFIG = os.environ.get('SKIP_CONFIG') == 'true'
COMMIT_MESSAGE = os.environ.get(
    'COMMIT_MESSAGE', 'GitLab-native CI/CD infrastructure')
TOKEN = os.environ.get('GITLAB_TOKEN', '')

API = f'{HOST}/api/v4'
PKG = os.path.dirname(os.path.abspath(__file__))

# Files committed to the repository, relative to the repo root.
REPO_FILES = [
    '.gitlab-ci.yml',
    '.gitlab/issue_templates/bug_report.md',
    '.gitlab/issue_templates/documentation.md',
    '.gitlab/issue_templates/feature_request.md',
    '.gitlab/issue_templates/theorem_proposal.md',
    '.gitlab/issue_templates/verification_failure.md',
    '.gitlab/merge_request_templates/Default.md',
    '.gitlab/merge_request_templates/Theorem_or_Monograph.md',
    'CODEOWNERS',
    'GITLAB_SETUP.md',
    'README.md',
    'CHANGELOG.md',
    'SECURITY.md',
    'requirements-dev.txt',
]

# Wiki pages: (local file, title, slug)
WIKI_PAGES = [
    ('wiki/Home.md', 'Home'),
    ('wiki/CI-CD-Pipeline.md', 'CI-CD Pipeline'),
    ('wiki/Verification-Matrix.md', 'Verification Matrix'),
]

LABELS = [
    ('bug', '#D9534F', 'Something is broken in the verification suite'),
    ('enhancement', '#428BCA', 'New feature or new verification mode'),
    ('documentation', '#1284BA', 'Docs, README, Pages content'),
    ('verification', '#8B5CF6', 'Protocol V1–V9 / certificates / backend runs'),
    ('theorem', '#7B68EE', 'Theorem monograph or certificate proposal (T-series)'),
    ('security', '#C0392B', 'Security-relevant issue (also handled confidentially)'),
    ('release', '#2EA043', 'Release preparation and tag pipelines'),
    ('needs-triage', '#F0AD4E', 'Awaiting maintainer classification'),
]

BADGES = [
    ('pipeline', 'Pipeline (main)',
     '{base}/badges/{branch}/pipeline.svg', '{base}/-/pipelines'),
    ('coverage', 'Coverage (pytest)',
     '{base}/badges/{branch}/coverage.svg', '{base}/-/graphs/{branch}'),
    ('release', 'Latest release',
     '{base}/-/badges/release.svg', '{base}/-/releases'),
]

PROJECT_SETTINGS = {
    'only_allow_merge_if_pipeline_succeeds': True,
    'remove_source_branch_after_merge': True,
    'issues_enabled': True,
    'merge_requests_enabled': True,
    'wiki_enabled': True,
    'snippets_enabled': True,
    'repository_enabled': True,
    'topics': ['mathematics', 'hodge-conjecture', 'verification',
               'lean4', 'scientific-computing', 'number-theory',
               'monograph'],
}

SCHEDULE = {
    'description': 'Nightly full verification suite (plots + polyglot + pip-audit)',
    'ref': 'main',
    'cron': '30 2 * * *',
    'cron_timezone': 'UTC',
    'active': True,
}

GREEN, RED, YELLOW, DIM, OFF = '\033[1;32m', '\033[1;31m', '\033[1;33m', '\033[2m', '\033[0m'


# ═════════════════════════════════════════════════════════════════════════════
def api(method: str, path: str, payload: dict | None = None,
        ok: tuple = (200, 201), quiet_fail: bool = False):
    """Single API call. Returns (ok, status, body_dict_or_text)."""
    url = f'{API}/{path.lstrip("/")}'
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('PRIVATE-TOKEN', TOKEN)
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode()
            status = resp.status
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors='replace')
        status = exc.code
    except urllib.error.URLError as exc:
        print(f'{RED}  network error: {exc.reason}{OFF}')
        sys.exit(1)
    try:
        parsed = json.loads(body) if body else {}
    except json.JSONDecodeError:
        parsed = body
    good = status in ok
    if not good and not quiet_fail:
        msg = parsed if isinstance(parsed, str) else json.dumps(
            parsed.get('message', parsed), ensure_ascii=False)[:300]
        print(f'{YELLOW}  HTTP {status}: {msg}{OFF}')
    return good, status, parsed


def step(title: str) -> None:
    print(f'\n{YELLOW}▸ {title}{OFF}')


def note(text: str) -> None:
    print(f'{DIM}  {text}{OFF}')


def done(text: str) -> None:
    print(f'{GREEN}  ✔ {text}{OFF}')


def warn(text: str) -> None:
    print(f'{YELLOW}  ! {text}{OFF}')


def check_token() -> None:
    step('Checking token')
    ok, status, user = api('GET', 'user', ok=(200,))
    if not ok or not isinstance(user, dict):
        print(f'{RED}Token rejected (HTTP {status}). Need a PAT with `api` '
              f'scope and Maintainer role on the project.{OFF}')
        sys.exit(1)
    done(f'authenticated as {user.get("username")} ({user.get("name")})')
    ok, status, proj = api('GET', f'projects/{PROJECT_ID}',
                           {'simple': True}, ok=(200,))
    if not ok or not isinstance(proj, dict):
        print(f'{RED}Project {PROJECT_ID} not reachable (HTTP {status}).{OFF}')
        sys.exit(1)
    done(f'project: {proj.get("path_with_namespace")} '
         f'(default branch: {proj.get("default_branch")})')


# ═══════════════════════════════════ phase 1: push ══════════════════════════
def build_actions() -> list:
    actions = []
    for rel in REPO_FILES:
        local = os.path.join(PKG, rel)
        if not os.path.isfile(local):
            print(f'{RED}missing package file: {rel}{OFF}')
            sys.exit(1)
        with open(local, 'rb') as fh:
            content = base64.b64encode(fh.read()).decode()
        ok, status, _ = api(
            'GET',
            f'projects/{PROJECT_ID}/repository/files/'
            f'{urllib.parse.quote(rel, safe="")}',
            {'ref': DEFAULT_BRANCH}, ok=(200,), quiet_fail=True)
        action = 'update' if ok else 'create'
        actions.append({'action': action, 'file_path': rel,
                        'content': content, 'encoding': 'base64'})
        print(f'{DIM}  {action:<6} {rel}{OFF}')
    return actions


def push_files() -> None:
    global SKIP_PUSH
    step(f'Phase 1 — commit {len(REPO_FILES)} files to "{TARGET_BRANCH}"')
    if DRY_RUN:
        note('dry run — building the action list only')
        build_actions()
        done('plan complete (dry run)')
        SKIP_PUSH = True
        return
    actions = build_actions()
    payload = {
        'branch': TARGET_BRANCH,
        'commit_message': COMMIT_MESSAGE,
        'actions': actions,
    }
    if TARGET_BRANCH != DEFAULT_BRANCH:
        payload['start_branch'] = DEFAULT_BRANCH
    ok, status, result = api(
        'POST', f'projects/{PROJECT_ID}/repository/commits', payload,
        ok=(200, 201))
    if not ok:
        print(f'{RED}commit failed (HTTP {status}) — token scope or '
              f'protection may block direct push to {TARGET_BRANCH}.{OFF}')
        sys.exit(1)
    done(f'commit {str(result.get("id"))[:12]} → '
         f'{result.get("web_url", "")}')
    if OPEN_MR:
        mr_payload = {
            'source_branch': TARGET_BRANCH,
            'target_branch': DEFAULT_BRANCH,
            'title': 'GitLab-native CI/CD: full pipeline, templates, security, releases',
            'remove_source_branch': True,
            'description': ('Delivered by `push_to_gitlab.sh` from the GitLab '
                            'infrastructure package. See `GITLAB_SETUP.md` '
                            'for the feature list and the remaining manual '
                            'steps. CI will run the full verification matrix '
                            'on this MR.'),
        }
        ok, status, mr = api(
            'POST', f'projects/{PROJECT_ID}/merge_requests', mr_payload,
            ok=(200, 201), quiet_fail=True)
        if ok:
            done(f'MR !{mr.get("iid")}: {mr.get("web_url")}')
        else:
            warn('MR not created (maybe one already exists for this branch)')


# ══════════════════════════════════ phase 2: config ═════════════════════════
def configure() -> None:
    if SKIP_CONFIG:
        note('phase 2 skipped (--skip-config)')
        return
    step('Phase 2 — project configuration')

    # ── project settings ──
    ok, _, _ = api('PUT', f'projects/{PROJECT_ID}', PROJECT_SETTINGS)
    if ok:
        done('merge settings: pipeline must succeed, source branch removed')
        done('topics: ' + ', '.join(PROJECT_SETTINGS['topics']))
    else:
        warn('could not update project settings (token role too low?)')

    # ── protected branch ──
    ok, _, _ = api('POST', f'projects/{PROJECT_ID}/protected_branches', {
        'name': DEFAULT_BRANCH, 'push_access_level': 40,
        'merge_access_level': 40, 'allow_force_push': False,
        'code_approval_required': True,
    }, quiet_fail=True)
    if ok:
        done(f'branch "{DEFAULT_BRANCH}" protected (push/merge: Maintainers)')
    else:
        note(f'branch "{DEFAULT_BRANCH}" already protected or unsupported '
             f'option — skipping')

    # ── protected tags ──
    ok, _, _ = api('POST', f'projects/{PROJECT_ID}/protected_tags', {
        'name': 'v*', 'create_access_level': 40,
    }, quiet_fail=True)
    if ok:
        done('tags "v*" protected (only Maintainers create releases)')
    else:
        note('protected tag "v*" already exists — skipping')

    # ── badges ──
    base = f'{HOST}/wild8highlander1/hodge-laboratory'
    ok, _, existing = api('GET', f'projects/{PROJECT_ID}/badges')
    have = {b.get('name') for b in existing} if ok and isinstance(existing, list) else set()
    for key, name, img_t, link_t in BADGES:
        if key in have:
            note(f'badge "{key}" already exists — skipping')
            continue
        ok, _, _ = api('POST', f'projects/{PROJECT_ID}/badges', {
            'name': key,
            'image_url': img_t.format(base=base, branch=DEFAULT_BRANCH),
            'link_url': link_t.format(base=base, branch=DEFAULT_BRANCH),
        }, quiet_fail=True)
        if ok:
            done(f'badge "{key}" added')
        else:
            warn(f'badge "{key}" not added')

    # ── nightly schedule ──
    ok, _, schedules = api('GET', f'projects/{PROJECT_ID}/pipeline_schedules')
    names = [s.get('description') for s in schedules] if ok and isinstance(schedules, list) else []
    if SCHEDULE['description'] in names:
        note('nightly schedule already exists — skipping')
    else:
        ok, _, _ = api('POST', f'projects/{PROJECT_ID}/pipeline_schedules',
                       SCHEDULE, quiet_fail=True)
        if ok:
            done(f'nightly schedule created ({SCHEDULE["cron"]} UTC) — '
                 'activate it in CI/CD → Schedules if it was created inactive')
        else:
            warn('nightly schedule not created — create it manually '
                 '(CI/CD → Schedules, ref main, cron "30 2 * * *")')

    # ── labels ──
    ok, _, existing = api('GET', f'projects/{PROJECT_ID}/labels')
    have = {l.get('name') for l in existing} if ok and isinstance(existing, list) else set()
    for name, color, desc in LABELS:
        if name in have:
            note(f'label "{name}" already exists — skipping')
            continue
        ok, _, _ = api('POST', f'projects/{PROJECT_ID}/labels', {
            'name': name, 'color': color, 'description': desc,
        }, quiet_fail=True)
        if ok:
            done(f'label "{name}" added')
        else:
            warn(f'label "{name}" not added')

    # ── MR approvals (best effort; multiple rules need Premium) ──
    ok, _, approvals = api('GET', f'projects/{PROJECT_ID}/approvals',
                           ok=(200,), quiet_fail=True)
    if ok and isinstance(approvals, dict):
        if approvals.get('approvals_required') == 1:
            note('1 approval already required — skipping')
        else:
            ok2, _, _ = api('PUT', f'projects/{PROJECT_ID}/approvals',
                            {'approvals_required': 1}, quiet_fail=True)
            if ok2:
                done('MR approvals: 1 required')
            else:
                note('MR approvals not available on this tier — '
                     'optional manual step')
    else:
        note('MR approvals API unavailable on this tier — optional manual step')

    # ── wiki ──
    ok, _, pages = api('GET', f'projects/{PROJECT_ID}/wikis?with_content=0',
                       ok=(200,), quiet_fail=True)
    existing = {}
    if ok and isinstance(pages, list):
        existing = {p.get('title', '').lower(): p.get('slug') for p in pages}
    for local, title in WIKI_PAGES:
        path = os.path.join(PKG, local)
        if not os.path.isfile(path):
            warn(f'wiki source missing: {local}')
            continue
        content = open(path, encoding='utf-8').read()
        payload = {'title': title, 'content': content, 'format': 'markdown'}
        slug = existing.get(title.lower())
        if slug:
            ok, _, _ = api('PUT', f'projects/{PROJECT_ID}/wikis/'
                           f'{urllib.parse.quote(slug, safe="")}', payload,
                           quiet_fail=True)
        else:
            ok, _, _ = api('POST', f'projects/{PROJECT_ID}/wikis', payload,
                           quiet_fail=True)
        if ok:
            done(f'wiki page "{title}" {"updated" if slug else "created"}')
        else:
            warn(f'wiki page "{title}" failed (wiki disabled?)')


# ══════════════════════════════════════ main ════════════════════════════════
def main() -> None:
    if not TOKEN:
        print('GITLAB_TOKEN is empty.')
        sys.exit(1)
    print('═════════════════════════════════════════════════════════════')
    print(' HODGE LABORATORY → GitLab  (package delivery + provisioning)')
    print('═════════════════════════════════════════════════════════════')
    check_token()
    if not SKIP_PUSH:
        push_files()
    else:
        note('phase 1 skipped (--skip-push)')
    if DRY_RUN:
        note('dry run — configuration not executed')
    else:
        configure()
    print('\n═════════════════════════════════════════════════════════════')
    proj_url = f'{HOST}/wild8highlander1/hodge-laboratory'
    print(f' {GREEN}Done.{OFF} Next places to look:')
    print(f'   • Pipelines      {proj_url}/-/pipelines')
    print(f'   • Pages (docs/)  https://wild8highlander1.gitlab.io/hodge-laboratory/')
    print(f'   • Vulnerabilities {proj_url}/-/security/vulnerability_report')
    print(f'   • Wiki           {proj_url}/-/wikis')
    print(f'   Remaining manual steps: see GITLAB_SETUP.md in the repo.')
    print('═════════════════════════════════════════════════════════════')


if __name__ == '__main__':
    main()
