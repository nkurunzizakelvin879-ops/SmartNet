import os
import unittest
from unittest.mock import patch

from app import create_app
from extensions import db
from models import User


class SmartNetAuthTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            "DATABASE_URL": "sqlite://",
            "ADMIN_EMAIL": "test-admin@smartnet.local",
            "ADMIN_PASSWORD": "TestPassword123!",
            "SECRET_KEY": "test-secret-key",
        })
        self.env.start()
        self.app = create_app()
        self.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.env.stop()

    def test_login_page_loads(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_protected_dashboard_redirects_when_logged_out(self):
        response = self.client.get("/dashboard")
        self.assertIn(response.status_code, (302, 303))
        self.assertIn("/login", response.headers.get("Location", ""))

    def test_invalid_password_does_not_authenticate(self):
        response = self.client.post("/login", data={
            "email": "test-admin@smartnet.local",
            "password": "wrong-password",
        })
        self.assertIn(response.status_code, (200, 302))
        dashboard = self.client.get("/dashboard")
        self.assertIn(dashboard.status_code, (302, 303))

    def test_valid_login_opens_dashboard(self):
        response = self.client.post("/login", data={
            "email": "test-admin@smartnet.local",
            "password": "TestPassword123!",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Network Dashboard", response.data)

    def test_logout_requires_post(self):
        self.client.post("/login", data={
            "email": "test-admin@smartnet.local",
            "password": "TestPassword123!",
        })
        response = self.client.get("/logout")
        self.assertEqual(response.status_code, 405)


if __name__ == "__main__":
    unittest.main()
