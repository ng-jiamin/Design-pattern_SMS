"""Behavioural design pattern: Strategy (three interchangeable searches)."""
from abc import ABC, abstractmethod
from models import Student

# Refactoring improvement: Conditional complexity.
# Separate search strategies allow interchangeable
# algorithms without expanding a single search method.

class SearchStrategy(ABC):
    @abstractmethod
    def search(self, students: list[Student], keyword: str) -> list[Student]:
        """Return all matching students."""


class SearchByID(SearchStrategy):
    def search(self, students, keyword):
        return [student for student in students if student.student_id == keyword]


class SearchByName(SearchStrategy):
    def search(self, students, keyword):
        return [student for student in students if keyword.casefold() in student.name.casefold()]


class SearchByProgramme(SearchStrategy):
    def search(self, students, keyword):
        return [student for student in students if keyword.casefold() in student.programme.casefold()]
