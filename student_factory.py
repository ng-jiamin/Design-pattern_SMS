"""Creational design pattern: Factory Method."""
from abc import ABC, abstractmethod
from models import BusinessStudent, ComputingStudent, Student

# Code smell addressed: Duplicated object creation.
# Factory Method centralizes student object creation
# and reduces coupling to concrete student classes.

class StudentCreator(ABC):
    @abstractmethod
    def create_student(self, student_id, name, programme, dob, cgpa) -> Student:
        """Concrete creators implement this method to create concrete student types"""

class BusinessStudentCreator(StudentCreator):
    def create_student(self, student_id, name, programme, dob, cgpa) -> Student:
        return BusinessStudent(student_id, name, programme, dob, cgpa)


class ComputingStudentCreator(StudentCreator):
    def create_student(self, student_id, name, programme, dob, cgpa) -> Student:
        return ComputingStudent(student_id, name, programme, dob, cgpa)


class StudentFactory:
    """Selects a creator; StudentService need not use concrete student classes"""

    def __init__(self):
        self.creators = {
            "Business": BusinessStudentCreator(),
            "Computing": ComputingStudentCreator(),
        }

    def create_student(self, student_id, name, programme, dob, cgpa) -> Student:
        creator = self.creators.get(programme)
        if creator is None:
            raise ValueError("Unsupported student programme.")
        return creator.create_student(student_id, name, programme, dob, cgpa)
