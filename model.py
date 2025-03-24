import os
import datetime
import pdfplumber
from transformers import pipeline

# Suppress TensorFlow warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Load the model with error handling
try:
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", revision="d7645e1")


    print(classifier("Test document", candidate_labels=["high", "medium", "low"]))
except Exception as e:
    print(f"❌ Error loading model: {e}")
    classifier = None

# Urgency categories
categories = ["high", "medium", "low"]

# Weights for classification
SOURCE_WEIGHTS = {"central office": 1.0, "regional office": 0.8, "division office": 0.6, "school level": 0.4}
TYPE_WEIGHTS = {"memorandum": 1.0, "request for participants": 0.7, "general notice": 0.5, "other": 0.3}
CONFIDENTIALITY_WEIGHT = 1.2
FINANCIAL_WEIGHT = 1.1

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
            print(f"Extracted text from {pdf_path}:\n{text[:500]}")  # Show first 500 chars
            if not text.strip():
                print(f"Error: No text extracted from {pdf_path}")
            return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def classify_urgency(document_text, deadline, source, doc_type, is_confidential, is_financial):
    """Classifies the urgency of a document based on text and metadata."""
    if not document_text.strip():
        print("❌ Error: Document text is empty.")
        return {"category": "low", "score": 0.0}

    if not classifier:
        print("❌ Error: Model not loaded properly.")
        return {"error": "Model loading failed"}

    try:
        # Get AI-based classification scores
        result = classifier(document_text, candidate_labels=categories)

        # Debugging: Print raw output from the model
        print("🔍 Model raw output:", result)

        if not isinstance(result, dict) or "labels" not in result or "scores" not in result:
            print("❌ Error: Invalid model output structure:", result)
            return {"error": "Invalid model output"}
        
        if not result or "labels" not in result or "scores" not in result:
            print("Error: Invalid model output.")
            return {"error": "Invalid model output"}

        scores = {label: score for label, score in zip(result["labels"], result["scores"])}
        
        # Get AI-based urgency score
        ai_score = scores.get("high", 0.0) * 100

        # Apply metadata weights
        source_weight = SOURCE_WEIGHTS.get(source.lower(), 0.5)
        type_weight = TYPE_WEIGHTS.get(doc_type.lower(), 0.5)
        confidential_weight = CONFIDENTIALITY_WEIGHT if is_confidential else 1.0
        financial_weight = FINANCIAL_WEIGHT if is_financial else 1.0
        
        # Calculate total urgency score
        urgency_score = min(ai_score * source_weight * type_weight * confidential_weight * financial_weight, 100)

        return {"category": max(scores, key=scores.get), "score": urgency_score}

    except Exception as e:
        print(f"Error in classify_urgency: {e}")
        return {"error": str(e)}

def process_documents(folder_path):
    """Processes all PDFs in the given folder and returns urgency reports sorted by priority."""
    category_priority = {"high": 3, "medium": 2, "low": 1}
    
    urgency_reports = []  # Initialize the list here

    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            text = extract_text_from_pdf(file_path)

            # Example metadata (you can customize these)
            urgency_result = classify_urgency(text, "2025-03-20", "Central Office", "Memorandum", True, False)
            
            urgency_reports.append({
                "document": filename,
                "urgency_category": urgency_result.get("category", "low"),
                "urgency_score": urgency_result.get("score", 0.0)
            })

    # Sort the list AFTER it has been populated
    urgency_reports.sort(
        key=lambda x: (category_priority.get(x["urgency_category"], 0), x["urgency_score"]),
        reverse=True
    )

    return urgency_reports  # Return the sorted results

# Example usage
# sorted_urgency = process_documents(folder_path)


# Display the sorted results
sorted_urgency = process_documents("C:/Users/LAARNIESTRADA/Documents/Thesis/SDUPS_Test6/SDUPS_Backend/uploads")
for doc in sorted_urgency:
    print(f"{doc['document']} → {doc['urgency_category']} (Score: {doc['urgency_score']:.2f})")
