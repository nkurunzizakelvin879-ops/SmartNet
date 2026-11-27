import unittest

from app import create_app
from extensions import db
from models import User, Device, Customer


class SmartNetAuthTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "ADMIN_EMAIL": "test-admin@smartnet.local",
            "ADMIN_PASSWORD": "TestPassword123!",
            "SECRET_KEY": "test-secret-key",
        })
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_login_page_loads(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_protected_dashboard_redirects_when_logged_out(self):
        response = self.client.get("/dashboard")
        self.assertIn(response.status_code, (302, 303))
        self.assertIn("/login", response.headers.get("Location", ""))

    def test_invalid_password_does_not_authenticate(self):
        self.client.post("/login", data={
            "email": "test-admin@smartnet.local",
            "password": "wrong-password",
        })
        dashboard = self.client.get("/dashboard")
        self.assertIn(dashboard.status_code, (302, 303))

    def test_valid_login_opens_dashboard(self):
        response = self.client.post("/login", data={
            "email": "test-admin@smartnet.local",
            "password": "TestPassword123!",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Network Dashboard", response.data)


    def login_as_staff(self):
        with self.app.app_context():
            staff = User(full_name="Test Staff", email="staff@smartnet.local", role="staff")
            staff.set_password("StaffPassword123!")
            db.session.add(staff)
            device = Device(name="Test Router", device_type="Router", ip_address=None)
            customer = Customer(full_name="Test Customer", monthly_fee=10)
            db.session.add_all([device, customer])
            db.session.commit()
            device_id, customer_id = device.id, customer.id
        self.client.post("/login", data={"email":"staff@smartnet.local","password":"StaffPassword123!"})
        return device_id, customer_id

    def test_staff_cannot_delete_device(self):
        device_id, _ = self.login_as_staff()
        response = self.client.post(f"/devices/{device_id}/delete", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertIsNotNone(db.session.get(Device, device_id))

    def test_staff_cannot_delete_customer(self):
        _, customer_id = self.login_as_staff()
        response = self.client.post(f"/customers/{customer_id}/delete", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertIsNotNone(db.session.get(Customer, customer_id))

    def test_logout_requires_post(self):
        self.client.post("/login", data={
            "email": "test-admin@smartnet.local",
            "password": "TestPassword123!",
        })
        response = self.client.get("/logout")
        self.assertEqual(response.status_code, 405)


if __name__ == "__main__":
    unittest.main()
