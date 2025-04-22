import json, requests, os
from pathlib import Path

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def create_labels(repo_url: str, labels: list[dict]):
    api_base = f"https://api.github.com/repos/{repo_url}/labels"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    for lbl in labels:
        resp = requests.post(api_base, headers=headers, json=lbl)
        if resp.status_code == 201:
            print(f"✅ Created label {lbl['name']}")
        else:
            print(f"❌ Failed {lbl['name']}: {resp.status_code}", resp.json())

if __name__ == "__main__":
    # read tags.json from the same directory as this script
    tags_file = Path(__file__).parent / "tags.json"
    data = json.loads(tags_file.read_text())
    tags = data.get("tags", [])

    new_labels = [
        {
            "name": t["name"],
            "description": t.get("description", ""),
            "color": t.get("color", "ededed")
        }
        for t in tags
        if "name" in t
    ]

    create_labels("bethanyjep/build-your-first-agent", new_labels)