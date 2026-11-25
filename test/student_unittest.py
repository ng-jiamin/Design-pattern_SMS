
import unittest
from unittest.mock import Mock
from datetime import date

import sys
import os

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

from models import BusinessStudent, ComputingStudent
from student_factory import StudentFactory
from student_service import StudentService
from validation import ValidationError


class TestSearchStudents(unittest.TestCase):

    def setUp(self):
        self.students = [
            ComputingStudent('12345', 'Carmen Ng', 'Computing',
                             date(2006, 12, 1), 3.5),
            BusinessStudent('29313', 'Jia Min Ng', 'Business',
                            date(2010, 6, 8), 3.8),
            ComputingStudent('93289', 'Ashley', 'Computing',
                             date(2009, 2, 28), 4.0),
        ]

        repository = Mock()
        repository.load_students.return_value = self.students
        self.service = StudentService(repository, StudentFactory())

    def test_search_by_id(self):
        result = self.service.search_students('id', '12345')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Carmen Ng')

    def test_search_by_name_case_insensitive(self):
        result = self.service.search_students('name', 'CARMEN')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['student_id'], '12345')

    def test_search_by_programme(self):
        result = self.service.search_students('programme', 'computing')
        self.assertEqual(len(result), 2)
        self.assertEqual(
            {student['student_id'] for student in result},
            {'12345', '93289'}
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
        result = self.service.search_students('name', 'Ng')
        self.assertEqual(
            {student['student_id'] for student in result},
            {'12345', '29313'}
        )


if __name__ == '__main__':
    unittest.main()
