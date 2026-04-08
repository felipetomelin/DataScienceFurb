"""
github_upload.py
─────────────────────────────────────────────────────────────────────────────
Faz upload dos arquivos gerados para o repositório GitHub via API REST.
Mais robusto que o shell script — lida melhor com encoding e SHA updates.

USO:
    pip install requests
    export GITHUB_TOKEN="ghp_seu_token_aqui"
    python3 github_upload.py

    # ou passando o token diretamente:
    python3 github_upload.py --token ghp_seu_token_aqui
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import base64
import argparse
import requests

# ─── Config ───────────────────────────────────────────────────────────────────
REPO = "felipetomelin/DataScienceFurb"
BRANCH = "main"
API_BASE = f"https://api.github.com/repos/{REPO}/contents"

# Files to upload: (local_path, remote_path, commit_message)
FILES_TO_UPLOAD = [
    (
        "README.md",
        "README.md",
        "docs: update main README with project structure and setup guide"
    ),
    (
        "docs/DATA_DICTIONARY.md",
        "docs/DATA_DICTIONARY.md",
        "docs: add complete Data Dictionary after data preparation"
    ),
    (
        "notebooks/data_preparation.py",
        "notebooks/data_preparation.py",
        "feat: add Data Preparation pipeline (ETL) — step 1 of project"
    ),
]
# ──────────────────────────────────────────────────────────────────────────────


def get_file_sha(path: str, token: str) -> str | None:
    """Return the SHA of a file in the repo, or None if it doesn't exist."""
    url = f"{API_BASE}/{path}?ref={BRANCH}"
    r = requests.get(url, headers={"Authorization": f"token {token}"})
    if r.status_code == 200:
        return r.json().get("sha")
    return None


def upload_file(local_path: str, remote_path: str, commit_msg: str, token: str) -> bool:
    """Upload a single file to GitHub. Returns True on success."""
    if not os.path.exists(local_path):
        print(f"  ⚠️  Local file not found: {local_path}")
        return False

    with open(local_path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode("utf-8")

    sha = get_file_sha(remote_path, token)

    payload = {
        "message": commit_msg if not sha else f"{commit_msg} (update)",
        "content": content_b64,
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha

    url = f"{API_BASE}/{remote_path}"
    r = requests.put(
        url,
        json=payload,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        },
    )

    if r.status_code in (200, 201):
        action = "Updated" if sha else "Created"
        print(f"  ✅ {action}: {remote_path}")
        return True
    else:
        print(f"  ❌ Failed ({r.status_code}): {remote_path}")
        print(f"     {r.json().get('message', 'Unknown error')}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Upload files to GitHub repo via API")
    parser.add_argument("--token", help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)")
    args = parser.parse_args()

    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("❌ GitHub token not found.")
        print("   Set GITHUB_TOKEN env var or pass --token ghp_...")
        sys.exit(1)

    print(f"🚀 Uploading to: https://github.com/{REPO} (branch: {BRANCH})")
    print(f"   {len(FILES_TO_UPLOAD)} file(s) to process\n")

    # Change to the directory of this script so relative paths work
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(script_dir))  # go up to DataScienceFurb/

    success = 0
    for local_path, remote_path, commit_msg in FILES_TO_UPLOAD:
        print(f"→ {remote_path}")
        if upload_file(local_path, remote_path, commit_msg, token):
            success += 1

    print(f"\n{'='*50}")
    print(f"✅ Done: {success}/{len(FILES_TO_UPLOAD)} files uploaded successfully")
    print(f"   Repository: https://github.com/{REPO}")


if __name__ == "__main__":
    main()
