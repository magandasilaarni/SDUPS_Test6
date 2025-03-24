from flask import Flask, request, render_template, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename
from sqlalchemy import case
from datetime import datetime
import os
import pdfplumber
import shutil
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import fitz
from model import classify_urgency

# Initialize Flask app
app = Flask(__name__, template_folder="templates")
CORS(app)

# Flask Configuration
BASE_UPLOAD_DIR = r"C:\Users\LAARNIESTRADA\Documents\Thesis\SDUPS_Test6\Documents"

def get_upload_folder():
    """Generates a folder path based on the current year and month."""
    current_year = datetime.now().year
    current_month = datetime.now().strftime("%B")  # Full month name (e.g., "March")
    
    upload_folder = os.path.join(BASE_UPLOAD_DIR, str(current_year), current_month)
    
    # Ensure the folder exists
    os.makedirs(upload_folder, exist_ok=True)
    
    return upload_folder

# Store the upload folder once and use it everywhere
UPLOAD_FOLDER = get_upload_folder()
print(f"✅ Upload folder: {UPLOAD_FOLDER}")

# Flask Configuration
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/LAARNIESTRADA/Documents/Thesis/SDUPS_Test6/SDUPS_Backend/instance/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize Database
db = SQLAlchemy(app)

class PDFFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    urgency = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default="Pending")
    comments = db.Column(db.Text, default="")
    uploaded_by = db.Column(db.String(100), nullable=False, default="Unknown")
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PDFFile {self.filename}>"

# Ensure Tables Exist
with app.app_context():
    db.create_all()
    print("Database and tables created successfully!")
    print(f"Database file exists: {os.path.exists('C:/Users/LAARNIESTRADA/Documents/Thesis/SDUPS_Test6/SDUPS_Backend/instance/database.db')}")

# Define the classify_urgency_from_upload_folder function
def classify_urgency_from_upload_folder():
    """Classify urgency of files directly from the UPLOAD_FOLDER."""
    upload_folder = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        if os.path.isfile(file_path):
            text = extract_text_from_pdf(file_path)
            if not text.strip():
                print(f"Error: No text extracted from {file_path}")
            urgency_result = classify_urgency(text, None, None, None, None, None)
            print(f"{filename} → {urgency_result['category']} (Score: {urgency_result['score']:.2f})")

# Create a route to trigger the function
@app.route('/classify_urgency', methods=['GET'])
def classify_urgency_route():
    try:
        classify_urgency_from_upload_folder()
        return jsonify({"message": "Urgency classification completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_files_from_database():
    """Retrieve file paths and other relevant information from the database."""
    files = PDFFile.query.all()
    file_info = []
    for file in files:
        file_info.append({
            "id": file.id,
            "filename": file.filename,
            "file_path": file.file_path,
            "extracted_text": file.extracted_text,
            "urgency": file.urgency,
            "status": file.status,
            "uploaded_by": file.uploaded_by,
            "upload_time": file.upload_time
        })
    return file_info

def process_files_from_database():
    """Process files retrieved from the database."""
    files = get_files_from_database()
    for file in files:
        file_path = file["file_path"]
        text = extract_text_from_pdf(file_path)
        if not text.strip():
            print(f"Error: No text extracted from {file_path}")
        urgency_result = classify_urgency(text, None, None, None, None, None)
        print(f"{file['filename']} → {urgency_result['category']} (Score: {urgency_result['score']:.2f})")

@app.route('/process_files', methods=['GET'])
def process_files():
    try:
        process_files_from_database()
        return jsonify({"message": "Files processed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"message": "No file received."}), 400
        
        print("File received:", file.filename)
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        if not os.path.exists(file_path):
            return jsonify({"message": "File was not saved correctly."}), 500
        
        print("File saved successfully.")
        
        extracted_text = extract_text_from_pdf(file_path)
        print("Extracted text:", extracted_text[:200])
        
        if not extracted_text.strip():
            return jsonify({"message": "Error: Document text is empty."}), 400
        
        urgency_scores = classify_urgency(extracted_text, None, None, None, None, None)
        urgency_level = max(urgency_scores["scores"], key=urgency_scores["scores"].get)
        
        new_file = PDFFile(
            filename=filename,
            file_path=file_path,
            extracted_text=extracted_text,
            urgency=urgency_level,
            status="Pending",
            uploaded_by="TEST USER",
            upload_time=datetime.utcnow()
        )
        
        db.session.add(new_file)
        db.session.commit()
        
        print("New file added to database:", new_file)
        
        return jsonify({
            "message": "File uploaded successfully",
            "urgency_level": urgency_level
        })
    
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"message": f"Error: {str(e)}"}), 500

def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file, checking for scanned images."""
    try:
        with pdfplumber.open(file_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            
            if not text.strip():
                print(f"⚠️ Warning: {file_path} contains no selectable text. It may be a scanned document.")
                return ""
            
            print(f"Extracted text from {file_path}:\n{text[:500]}")  # Show first 500 chars
            return text
    except Exception as e:
        print(f"❌ Error extracting text from {file_path}: {e}")
        return ""

def perform_ocr(file_path):
    ocr_text = []
    try:
        images = convert_from_path(file_path)
        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img)
            img.close()  # Close image to free memory
            if text.strip():
                ocr_text.append(text)
        return ocr_text if ocr_text else ["No text extracted."]
    except Exception as e:
        print(f"OCR processing error: {e}")
        return ["No text extracted."]

@app.route('/api/queue', methods=['GET'])
def get_queue():
    try:
        urgency_case = case(
            (PDFFile.urgency == "Low", 0),
            (PDFFile.urgency == "Medium", 1),
            (PDFFile.urgency == "High", 2)
        )
        queue = PDFFile.query.order_by(urgency_case).all()
        if not queue:
            print("No files found in queue")
        for pdf in queue:
            print(f"File: {pdf.filename}, Urgency: {pdf.urgency}, Status: {pdf.status}")
        return jsonify([{
            "id": pdf.id,
            "filename": pdf.filename,
            "urgency": pdf.urgency,
            "status": pdf.status,
            "comments": pdf.comments,
            "uploaded_by": pdf.uploaded_by,
            "upload_time": pdf.upload_time.isoformat()
        } for pdf in queue])
    except Exception as e:
        print(f"Error retrieving queue: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/scan_all', methods=['GET'])
def scan_all_files():
    """ Scans all files in the database and updates urgency classification. """
    try:
        files = PDFFile.query.all()
        if not files:
            return jsonify({"message": "No files found in the database."}), 404

        for file in files:
            # Reclassify urgency
            urgency_scores = classify_urgency(file.extracted_text, None, None, None, None, None)
            urgency_level = max(urgency_scores["scores"], key=urgency_scores["scores"].get)

            # Update database record
            file.urgency = urgency_level

        db.session.commit()
        return jsonify({"message": "All files scanned and urgency updated."})

    except Exception as e:
        return jsonify({"message": f"Error scanning files: {str(e)}"}), 500
    
@app.route('/review/<int:file_id>', methods=['GET'])
def review_file(file_id):
    # Retrieve file from database
    pdf_file = PDFFile.query.get(file_id)
    if not pdf_file:
        return jsonify({"message": "File not found"}), 404

    file_path = pdf_file.file_path  # Get the stored path from DB

    if not os.path.exists(file_path):
        return jsonify({"message": "File is missing on the server"}), 404

    # Serve the PDF file for preview
    return send_file(file_path, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
