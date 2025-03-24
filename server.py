from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import re
from datetime import datetime

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "doc", "docx"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store file data and urgency results
uploaded_files = []

# Urgency Keywords
URGENCY_KEYWORDS = ["urgent", "immediate", "asap", "deadline", "important", "priority", "due date"]


def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def calculate_urgency(content):
    """Calculate urgency based on keywords and dates."""
    # Analyze dates
    today = datetime.now()
    date_score = 0

    date_matches = re.findall(r"\b(\d{4}-\d{2}-\d{2}|\b\w{3,9} \d{1,2}, \d{4})\b", content)
    for date_str in date_matches:
        try:
            if "-" in date_str:
                date = datetime.strptime(date_str, "%Y-%m-%d")
            else:
                date = datetime.strptime(date_str, "%B %d, %Y")

            days_until_due = (date - today).days
            if days_until_due < 0:
                continue  # Ignore past dates
            elif days_until_due <= 2:
                date_score += 2  # Very urgent
            elif days_until_due <= 7:
                date_score += 1  # Moderately urgent
        except ValueError:
            continue

    # Analyze keywords
    keyword_count = sum([content.lower().count(keyword) for keyword in URGENCY_KEYWORDS])
    keyword_score = min(keyword_count, 2)  # Cap score at 2

    total_score = date_score + keyword_score
    return "Urgent" if total_score >= 2 else "Not Urgent"


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Detect urgency
            urgency = calculate_urgency(content)

            # Store the file data and urgency
            uploaded_files.append({"filename": filename, "urgency": urgency})

            return jsonify({"message": "File uploaded successfully", "urgency": urgency})
        except Exception as e:
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500
    else:
        return jsonify({"error": "Invalid file type"}), 400


@app.route("/dashboard", methods=["GET"])
def dashboard():
    """Serve the dashboard with file data."""
    return jsonify({"files": uploaded_files})


if __name__ == "__main__":
    app.run(debug=True)
