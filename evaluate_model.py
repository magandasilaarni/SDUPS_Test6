import os
from model import extract_text_from_pdf, classify_urgency, process_documents

# Define sample PDF file paths (ensure these files exist in your directory)
sample_pdf_paths = [
    r"C:\Users\LAARNIESTRADA\Documents\Thesis\SDUPS_Test6\Documents\2025\March\IPCRF-2024.pdf",
    r"C:\Users\LAARNIESTRADA\Documents\Thesis\SDUPS_Test6\Documents]\DM111s2025_EVALUATION_OF_WORKPLACE_APPLICATION_PLAN_FOR_MASTER_TEACHERS_PROFESSIONAL_DEVELOPMENT_PROGRAM_2.0.pdf"]

# Test extract_text_from_pdf function
for pdf_path in sample_pdf_paths:
    print(f"Testing extract_text_from_pdf with {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    print(f"Extracted text: {text[:200]}...")  # Print first 200 characters for brevity

# Test classify_urgency function with sample text and metadata
sample_text = "This is a sample document text to test urgency classification."
urgency_result = classify_urgency(sample_text, "2025-03-20", "Central Office", "Memorandum", True, False)
print(f"Urgency result: {urgency_result}")

# Test process_documents function with a sample folder path
sample_folder_path = r"C:\Users\LAARNIESTRADA\Documents\Thesis\SDUPS_Test6\Documents\2025\March"
print(f"Testing process_documents with {sample_folder_path}")
sorted_urgency = process_documents(sample_folder_path)
for doc in sorted_urgency:
    print(f"{doc['document']} → {doc['urgency_category']} (Score: {doc['urgency_score']:.2f})")