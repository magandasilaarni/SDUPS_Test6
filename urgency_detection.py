import re
from datetime import datetime, timedelta

# Define urgency keywords
URGENCY_KEYWORDS = ["urgent", "immediate", "asap", "deadline", "important", "priority", "due date"]

def calculate_date_score(text):
    """
    Analyze the text for dates and calculate urgency based on proximity to today.
    """
    today = datetime.now()
    deadline_score = 0

    # Search for dates in the text (e.g., "January 15, 2025" or "2025-01-15")
    date_matches = re.findall(r'\b(\d{4}-\d{2}-\d{2}|\b\w{3,9} \d{1,2}, \d{4})\b', text)
    for date_str in date_matches:
        try:
            # Parse the date
            if "-" in date_str:
                date = datetime.strptime(date_str, "%Y-%m-%d")
            else:
                date = datetime.strptime(date_str, "%B %d, %Y")
            
            # Calculate urgency based on how close the date is to today
            days_until_due = (date - today).days
            if days_until_due < 0:
                continue  # Ignore past dates
            elif days_until_due <= 2:
                deadline_score += 2  # Very urgent
            elif days_until_due <= 7:
                deadline_score += 1  # Moderately urgent
        except ValueError:
            continue

    return deadline_score


def calculate_keyword_score(text):
    """
    Calculate a score based on the presence of urgency-related keywords.
    """
    keyword_count = sum([text.lower().count(keyword) for keyword in URGENCY_KEYWORDS])
    return min(keyword_count, 2)  # Limit the score to a maximum of 2


def determine_final_urgency(text):
    """
    Combine AI prediction, date score, and keyword score to determine urgency.
    """
    ai_score = 1 if determine_urgency(text) == "Urgent" else 0
    date_score = calculate_date_score(text)
    keyword_score = calculate_keyword_score(text)

    # Total score threshold to classify as Urgent
    total_score = ai_score + date_score + keyword_score
    return "Urgent" if total_score >= 2 else "Not Urgent"
