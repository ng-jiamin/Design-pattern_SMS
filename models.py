"""Student models. BusinessStudent and ComputingStudent are separate types."""
from abc import ABC, abstractmethod
from datetime import date

# Code smell addressed: Duplicated serialization logic.
# Shared student attributes and serialization methods
# are centralized in the base Student class.

class Student(ABC):
    """Common student details shared by both programmes."""

    def __init__(self, student_id: str, name: str, programme: str,
                 dob: date, cgpa: float):
        self.student_id = student_id
        self.name = name
        self.programme = programme
        self.dob = dob
        self.cgpa = cgpa

    def to_dict(self) -> dict:
        """Return student details for the website and the repository."""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "programme": self.programme,
            "dob": self.dob.isoformat(),
            "cgpa": self.cgpa,
        }

    @abstractmethod
    def display_details(self) -> dict:
        """Each concrete student type implements this method."""


class BusinessStudent(Student):
    def display_details(self) -> dict:
        return self.to_dict()


class ComputingStudent(Student):
    def display_details(self) -> dict:
        return self.to_dict()
