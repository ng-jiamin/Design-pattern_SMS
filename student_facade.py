"""Structural design pattern: Facade (single entry point for the website)."""
from student_service import StudentService

# Code smell addressed: Tight coupling.
# Facade provides a simplified interface between
# the presentation layer and business logic.

class StudentManagementFacade:
    def __init__(self, service: StudentService):
        self.service = service

    def list_students(self):
        return self.service.list_students()

    def search_students(self, by, keyword):
        return self.service.search_students(by, keyword)

    def add_student(self, data):
        return self.service.add_student(data)

    def update_student(self, student_id, data):
        return self.service.update_student(student_id, data)

    def delete_student(self, student_id):
        return self.service.delete_student(student_id)
