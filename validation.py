"""One place for validation shared by adding and updating students."""
from datetime import datetime
import math


class ValidationError(ValueError):
    """Invalid student details supplied by the user."""

# Code smell addressed: Duplicated validation logic.
# Shared validation rules ensure consistent checking
# during student creation and updating.

def validate_student(student_id, name, programme, dob, cgpa):
    """Validate and normalize values, following the original add-student rules."""
    student_id = str(student_id).strip()
    if len(student_id) != 5 or not all('0' <= digit <= '9' for digit in student_id):
        raise ValidationError("Student ID must contain exactly 5 digits.")

    name = str(name).strip()
    if len(name) <= 5 or not all(c.isalpha() or c.isspace() for c in name):
        raise ValidationError("Name must be longer than 5 characters and contain only letters and spaces.")

    programme_lookup = {"business": "Business", "b": "Business",
                        "computing": "Computing", "c": "Computing"}
    programme = programme_lookup.get(str(programme).strip().lower())
    if programme is None:
        raise ValidationError("Programme must be Business or Computing.")

    try:
        dob_date = datetime.strptime(str(dob).strip(), "%Y-%m-%d").date()
        if dob_date.isoformat() != str(dob).strip() or not 2000 <= dob_date.year <= 2024:
            raise ValueError("Date outside the allowed range or invalid format")
    except ValueError as exc:
        raise ValidationError("Date of birth must be a valid YYYY-MM-DD date between 2000 and 2024.") from exc

    try:
        cgpa_number = float(cgpa)
    except (TypeError, ValueError) as exc:
        raise ValidationError("CGPA must be a number between 0.00 and 4.00.") from exc
    if not math.isfinite(cgpa_number) or not 0.0 <= cgpa_number <= 4.0:
        raise ValidationError("CGPA must be a number between 0.00 and 4.00.")

    return student_id, name, programme, dob_date, round(cgpa_number, 2)
