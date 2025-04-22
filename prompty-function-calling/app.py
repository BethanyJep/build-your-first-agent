from flask import Flask, request, render_template
import json
from pathlib import Path
import os
import ast
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
            raw_tags = run(title, tags, description)
            
            # Process the response based on its type
            if isinstance(raw_tags, str):
                # If it's a string, try to parse it as JSON
                try:
                    categorized_tags = json.loads(raw_tags)
                except json.JSONDecodeError:
                    # If it's not valid JSON, try to evaluate it as a Python literal
                    try:
                        categorized_tags = ast.literal_eval(raw_tags)
                    except (ValueError, SyntaxError):
                        # If all else fails, split by commas and clean up
                        categorized_tags = [tag.strip(' "\'[]') for tag in raw_tags.split(',') if tag.strip(' "\'[]')]
            else:
                categorized_tags = raw_tags if raw_tags else []
                
        except Exception as e:
            return render_template("index.html", error=f"Error categorizing issue: {str(e)}")

        # Render the results
        return render_template("results.html", title=title, description=description, tags=categorized_tags)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)