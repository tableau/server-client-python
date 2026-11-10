import os
import subprocess

import requests

URL = "https://api.github.com/repos/tableau/server-client-python/contributors"


def github_token():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token
    try:
        return subprocess.check_output(["gh", "auth", "token"], text=True, stderr=subprocess.DEVNULL).strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def fetch_contributors():
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "getcontributors"}
    token = github_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    contributors = []
    page = 1
    while True:
        response = requests.get(URL, headers=headers, params={"per_page": 100, "page": page}, timeout=30)
        payload = response.json()
        if not response.ok or not isinstance(payload, list):
            message = payload.get("message", payload) if isinstance(payload, dict) else payload
            raise SystemExit(f"GitHub API error {response.status_code}: {message}")
        if not payload:
            break
        contributors.extend(payload)
        if len(payload) < 100:
            break
        page += 1
    return contributors


for person in fetch_contributors():
    login = person.get("login")
    html_url = person.get("html_url")
    if login and html_url:
        print(f"* [{login}]({html_url})")
