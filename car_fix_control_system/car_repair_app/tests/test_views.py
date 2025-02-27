from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User



class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.list_url = reverse('cars')
        

    def test_clients_list_get(self):
        response = self.client.get(self.list_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'cars.html')
