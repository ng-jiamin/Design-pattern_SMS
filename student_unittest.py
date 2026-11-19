
import unittest
from unittest.mock import Mock
from datetime import date

from models import BusinessStudent, ComputingStudent
from student_factory import StudentFactory
from student_service import StudentService
from validation import ValidationError


class TestSearchStudents(unittest.TestCase):

    def setUp(self):
        self.students = [
            ComputingStudent('12345', 'Alice Tan', 'Computing',
                             date(2003, 5, 10), 3.5),
            BusinessStudent('23456', 'Bob Smith', 'Business',
                            date(2002, 8, 20), 3.2),
            ComputingStudent('34567', 'Alicia Wong', 'Computing',
                             date(2004, 1, 15), 3.8),
        ]

        repository = Mock()
        repository.load_students.return_value = self.students
        self.service = StudentService(repository, StudentFactory())

    def test_search_by_id(self):
        result = self.service.search_students('id', '12345')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Alice Tan')

    def test_search_by_name_case_insensitive(self):
        result = self.service.search_students('name', 'ALICE')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['student_id'], '12345')

    def test_search_by_programme(self):
        result = self.service.search_students('programme', 'computing')
        self.assertEqual(len(result), 2)
        self.assertEqual(
            {student['student_id'] for student in result},
            {'12345', '34567'}
        )

    def test_search_with_no_match(self):
        result = self.service.search_students('name', 'Daniel')
        self.assertEqual(result, [])

    def test_search_with_invalid_type(self):
        with self.assertRaises(ValidationError):
            self.service.search_students('age', '20')

    def test_search_with_empty_keyword(self):
        with self.assertRaises(ValidationError):
            self.service.search_students('name', '   ')

    def test_search_with_invalid_id(self):
        with self.assertRaises(ValidationError):
            self.service.search_students('id', '123')

    def test_search_trims_whitespace(self):
        result = self.service.search_students('id', ' 12345 ')
        self.assertEqual(result[0]['student_id'], '12345')

    def test_search_by_partial_name(self):
        result = self.service.search_students('name', 'ali')
        self.assertEqual(
            {student['student_id'] for student in result},
            {'12345', '34567'}
        )


if __name__ == '__main__':
    unittest.main()
