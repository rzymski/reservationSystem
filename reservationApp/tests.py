from django.test import TestCase
from .models import *
from django.contrib.auth.models import User, Group
from django.urls import reverse, resolve


class TestForTests(TestCase):
    def testWorkOk(self):
        print("DZIALA TEST")


class MyTest(TestCase):
    def setUp(self):
        self.serviceProviderGroup = Group.objects.create(name='serviceProvider')
        self.user1 = User.objects.create_user(username='user1', password='testpass')
        self.user2 = User.objects.create_user(username='user2', password='testpass')
        self.user1.groups.add(self.serviceProviderGroup)
        self.user2.groups.add(self.serviceProviderGroup)

    def test_view_returns_correct_template_and_context(self):
        # Ustalamy URL widoku
        url = reverse('myTest')  # Wstaw nazwę rzeczywistego widoku
        # Symulujemy żądanie HTTP GET do widoku
        response = self.client.get(url)
        # Sprawdzamy, czy widok zwraca kod 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Sprawdzamy, czy widok używa oczekiwanego szablonu
        self.assertTemplateUsed(response, 'test/myTest.html')
        # Sprawdzamy, czy otrzymujemy oczekiwany kontekst
        reservations = response.context['reservations']
        availableBookingDates = response.context['availableBookingDates']
        self.assertEqual(len(reservations), 0)
        self.assertEqual(len(availableBookingDates), 1)
