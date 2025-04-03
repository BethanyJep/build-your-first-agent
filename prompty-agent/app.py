from flask import Flask, request, render_template
import json
from pathlib import Path
import os
# Import functions from basic.py
from basic import fetch_github_issues, run

# Initialize Flask app
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

@app.route("/", methods=["GET", "POST"])
def index():
    """Render the HTML form and handle form submissions."""
    if request.method == "POST":
        # Get the repository URL and tags.json file from the form
        repo_url = request.form.get("repo_url")
        tags_file = request.files.get("tags_file")

        if not repo_url or not tags_file:
            return render_template("index.html", error="Both fields are required.")

        # Save the uploaded tags.json file
        tags_path = Path(app.config["UPLOAD_FOLDER"]) / "tags.json"
        tags_path.parent.mkdir(parents=True, exist_ok=True)
        tags_file.save(tags_path)

        # Load tags from the uploaded file
        try:
            tags = json.loads(tags_path.read_text())["tags"]
        except Exception as e:
            return render_template("index.html", error=f"Error reading tags.json: {str(e)}")

        # Fetch a random issue from GitHub
        try:
            issue = fetch_github_issues(repo_url)
            if not issue:
                return render_template("index.html", error="No issues found in the repository.")
        except Exception as e:
            return render_template("index.html", error=f"Error fetching issues: {str(e)}")

        # Extract title and description from the random issue
        title = issue.get("title", "No Title")
        description = issue.get("body", "No Description")

        # Categorize the issue using basic.py's run function
        try:
            categorized_tags = run(title, tags, description)
            if not categorized_tags:
                categorized_tags = []
        except Exception as e:
            return render_template("index.html", error=f"Error categorizing issue: {str(e)}")

        # Render the results
        return render_template("results.html", title=title, description=description, tags=categorized_tags)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)