"""Repository layer: the only module that reads and writes student.txt."""
import csv
import os
from pathlib import Path
from student_factory import StudentFactory
from validation import validate_student


class StudentRepository:
    def __init__(self, filename: str | Path, factory: StudentFactory):
        self.filename = Path(filename)
        self.factory = factory

    def load_students(self) -> list:
        if not self.filename.exists():
            return []

        students = []
        try:
            with self.filename.open("r", encoding="utf-8", newline="") as file:
                for number, row in enumerate(csv.reader(file), start=1):
                    if not row:
                        continue
                    if len(row) != 5:
                        raise ValueError(f"Line {number} must contain 5 values.")
                    values = validate_student(*row)
                    students.append(self.factory.create_student(*values))
        except (OSError, ValueError) as exc:
            raise ValueError(f"Could not load {self.filename.name}: {exc}") from exc
        return students

    def save_students(self, students: list) -> None:
        """Write a temporary file first, so a failed save won't destroy records."""
        temp_file = self.filename.with_name(self.filename.name + ".tmp")
        try:
            with temp_file.open("w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file, lineterminator="\n")
                for student in students:
                    writer.writerow([student.student_id, student.name, student.programme,
                                     student.dob.isoformat(), student.cgpa])
            os.replace(temp_file, self.filename)
        except OSError as exc:
            raise OSError(f"Could not save {self.filename.name}: {exc}") from exc
        finally:
            if temp_file.exists():
                temp_file.unlink()
