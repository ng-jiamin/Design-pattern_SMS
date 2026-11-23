"""Service layer: student operations and business rules, no UI or file code."""
from student_factory import StudentFactory
from student_repository import StudentRepository
from search_strategy import SearchByID, SearchByName, SearchByProgramme
from validation import ValidationError, validate_student


class StudentNotFound(LookupError):
    pass


class DuplicateStudentID(ValidationError):
    pass


class StudentService:
    def __init__(self, repository: StudentRepository, factory: StudentFactory):
        self.repository = repository
        self.factory = factory
        self.students = self.repository.load_students()
        self.search_strategies = {
            "id": SearchByID(),
            "name": SearchByName(),
            "programme": SearchByProgramme(),
        }

    def list_students(self) -> list[dict]:
        return [student.display_details() for student in self.students]

    def search_students(self, by: str, keyword: str) -> list[dict]:
        """Strategy: choose an algorithm without adding new search conditionals."""
        strategy = self.search_strategies.get(by)
        if strategy is None:
            raise ValidationError("Search type must be id, name or programme.")
        keyword = keyword.strip()
        if not keyword:
            raise ValidationError("Please enter a search term.")
        if by == "id" and (len(keyword) != 5 or not keyword.isascii() or not keyword.isdigit()):
            raise ValidationError("Student ID must contain exactly 5 digits.")
        return [student.display_details() for student in strategy.search(self.students, keyword)]

    def _find(self, student_id):
        return next((student for student in self.students
                     if student.student_id == student_id), None)

    def add_student(self, data: dict) -> dict:
        values = validate_student(data.get("student_id", ""), data.get("name", ""),
                                  data.get("programme", ""), data.get("dob", ""),
                                  data.get("cgpa", ""))
        if self._find(values[0]):
            raise DuplicateStudentID("That Student ID already exists.")
        student = self.factory.create_student(*values) 
        updated = self.students + [student]
        self.repository.save_students(updated)
        self.students = updated
        return student.display_details()

    def update_student(self, student_id: str, data: dict) -> dict:
        old = self._find(student_id)
        if old is None:
            raise StudentNotFound("Student not found.")
        if "student_id" in data and str(data["student_id"]) != student_id:
            raise ValidationError("Student ID cannot be changed.")

        # Same rules as adding; re-create the correct subclass if programme changes.
        current = old.to_dict()
        current.update({key: value for key, value in data.items()
                        if key in {"name", "programme", "dob", "cgpa"}})
        values = validate_student(current["student_id"], current["name"],
                                  current["programme"], current["dob"], current["cgpa"])
        student = self.factory.create_student(*values)
        updated = [student if item.student_id == student_id else item for item in self.students]
        self.repository.save_students(updated)
        self.students = updated
        return student.display_details()

    def delete_student(self, student_id: str) -> None:
        if self._find(student_id) is None:
            raise StudentNotFound("Student not found.")
        updated = [student for student in self.students if student.student_id != student_id]
        self.repository.save_students(updated)
        self.students = updated
