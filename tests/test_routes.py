import pytest
from flask import url_for
from unittest.mock import patch
import unittest
from unittest.mock import patch, MagicMock
import unittest
from flask import Flask
from app import create_app  # Make sure this is the correct path to your app factory
import unittest
from app import create_app



class RoutesTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

    def test_student_dashboard(self):
        response = self.app.get('/student_dashboard', follow_redirects=True)
        self.assertIn(response.status_code, [200, 401])

    def test_advisor_dashboard_default(self):
        response = self.app.get('/advisor_dashboard', follow_redirects=True)
        self.assertIn(response.status_code, [200, 401])

    def test_toggle_calendar_view(self):
        response = self.app.post('/toggle_calendar_view', data={}, follow_redirects=True)
        self.assertIn(response.status_code, [200, 302, 401, 405])

    def test_get_advisors_api(self):
        response = self.app.get('/get_advisors')
        self.assertIn(response.status_code, [200, 404])

    def test_cancel_appointment(self):
        response = self.app.post('/cancel_appointment', data={"appointment_id": "1"}, follow_redirects=True)
        self.assertIn(response.status_code, [200, 302, 401, 405])

    def test_save_note(self):
        response = self.app.post('/save_note', data={"note": "Test Note"}, follow_redirects=True)
        self.assertIn(response.status_code, [200, 302, 401, 405])


if __name__ == '__main__':
    unittest.main()


