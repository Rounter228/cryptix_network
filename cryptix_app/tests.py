from django.test import TestCase


class CryptixTest(TestCase):
    def test_main(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)