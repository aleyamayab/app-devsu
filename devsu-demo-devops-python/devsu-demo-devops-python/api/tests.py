import json
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import User

class TestUserView(APITestCase):
    def setUp(self):
        self.user = User(name='Test1', dni='09876543210')
        self.user.save()
        self.url = reverse("users-list")
        self.data = {'name': 'Test2', 'dni': '09876543211'}

    def test_post(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, 201)
        payload = json.loads(response.content)
        self.assertEqual(payload["name"], "Test2")
        self.assertEqual(payload["dni"], "09876543211")
        self.assertIsInstance(payload.get("id"), int)
        self.assertEqual(User.objects.count(), 2)

    def test_get_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["id"], self.user.id)
        self.assertEqual(payload[0]["name"], "Test1")
        self.assertEqual(payload[0]["dni"], "09876543210")

    def test_get(self):
        response = self.client.get(reverse("users-detail", args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {"id": self.user.id, "name": "Test1", "dni": "09876543210"}
        )