import requests
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---- CONFIGURATION ----
# Token needs the "repo" scope (classic PAT) or "Administration: write"
# (fine-grained PAT) to change repo visibility.
GITHUB_TOKEN = ''  # <-- Place your token here, or use the env var below
GITHUB_USER = 'bell-kevin'

if not GITHUB_TOKEN:
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

# Safety switch: set to True to actually change visibility.
# Leave False for a dry run that only lists what *would* change.
DRY_RUN = True

# Optional: skip forks (often you don't want to flip forks public)
SKIP_FORKS = True

CPU_COUNT = os.cpu_count() or 4
MAX_WORKERS = min(16, CPU_COUNT * 2)  # be gentler than the merge script
print(f"Using {MAX_WORKERS} worker threads (detected {CPU_COUNT} logical CPUs).")

BASE_URL = 'https://api.github.com'
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
} if GITHUB_TOKEN else {}

session = requests.Session()
session.headers.update(HEADERS)

def handle_rate_limit(response):
    if response.status_code in (403, 429):
        remaining = response.headers.get('X-RateLimit-Remaining')
        if remaining == '0':
            reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 30))
            sleep_time = max(reset_time - int(time.time()), 0) + 1
            print(f"[RATE LIMIT] Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            return True
        # Secondary rate limit
        if 'retry-after' in {k.lower() for k in response.headers.keys()}:
            retry = int(response.headers.get('Retry-After', '5'))
            print(f"[SECONDARY LIMIT] Sleeping for {retry} seconds...")
            time.sleep(retry)
            return True
    return False

def request_with_retry(url, method='GET', **kwargs):
    while True:
        response = session.request(method, url, **kwargs)
        if handle_rate_limit(response):
            continue
        return response

def get_all_pages(url):
    while url:
        response = request_with_retry(url, method='GET', params={'per_page': 100})
        if response.status_code != 200:
            print(f"[ERROR] {url} -> {response.status_code}: {response.text}")
            break
        yield response.json()
        url = response.links.get('next', {}).get('url')

def get_all_repos():
    """Fetch all repos owned by the authenticated user (private + public)."""
    all_repos = []
    # affiliation=owner ensures we only get repos you own (not org/collab repos)
    url = f'{BASE_URL}/user/repos?affiliation=owner&visibility=all'
    for page in get_all_pages(url):
        all_repos.extend(page)
    return all_repos

def make_repo_public(repo):
    repo_name = repo['name']
    owner = repo['owner']['login']
    url = f'{BASE_URL}/repos/{owner}/{repo_name}'

    if DRY_RUN:
        return True, repo_name, 'would-make-public'

    response = request_with_retry(url, method='PATCH', json={'private': False})
    if response.status_code == 200:
        return True, repo_name, 'public'
    else:
        return False, repo_name, f"{response.status_code}: {response.text}"

def main():
    if not GITHUB_TOKEN:
        print("ERROR: set GITHUB_TOKEN in the script or as an environment variable.")
        return

    start_time = time.time()

    print("Fetching repositories...")
    all_repos = get_all_repos()
    print(f"Found {len(all_repos)} total repositories.")

    # Filter to repos that are currently private
    private_repos = [r for r in all_repos if r.get('private')]
    if SKIP_FORKS:
        before = len(private_repos)
        private_repos = [r for r in private_repos if not r.get('fork')]
        print(f"Skipping {before - len(private_repos)} forked repos.")

    print(f"{len(private_repos)} private repos will be flipped to public.")
    if DRY_RUN:
        print(">>> DRY RUN MODE — no changes will be made. Set DRY_RUN=False to apply. <<<")

    successes, failures = 0, 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(make_repo_public, r) for r in private_repos]
        for future in as_completed(futures):
            ok, name, info = future.result()
            if ok:
                print(f"[OK]   {name} -> {info}")
                successes += 1
            else:
                print(f"[FAIL] {name} -> {info}")
                failures += 1

    minutes, seconds = divmod(time.time() - start_time, 60)
    print(f"\nDone in {int(minutes)}m {seconds:.2f}s")
    print(f"Successes: {successes}  Failures: {failures}")

if __name__ == "__main__":
    main()
