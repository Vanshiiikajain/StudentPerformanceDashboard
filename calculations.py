# calculations.py
# Pure calculation logic — no database, no UI. Reused across the app.

MAX_MARKS_PER_SUBJECT = 100  # change this if your college uses a different scale


def calculate_result(subject1, subject2, subject3):
    """Takes 3 subject marks and returns (total, percentage, grade, result)."""
    total = subject1 + subject2 + subject3
    max_total = MAX_MARKS_PER_SUBJECT * 3
    percentage = round((total / max_total) * 100, 2)

    if percentage >= 90:
        grade = "A+"
    elif percentage >= 75:
        grade = "A"
    elif percentage >= 60:
        grade = "B"
    elif percentage >= 40:
        grade = "C"
    else:
        grade = "F"

    result = "Pass" if percentage >= 40 else "Fail"
    return total, percentage, grade, result