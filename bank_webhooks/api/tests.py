from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Organization, Payment
import uuid

class BankWebhookTests(TestCase):
    """Тесты для обработки входящих платежей от банка."""
    def setUp(self):
        self.client = APIClient()
        self.webhook_url = reverse('bank-webhook')
        self.sample_data = {
            "operation_id": "ccf0a86d-041b-4991-bcf7-e2352f7b8a4a",
            "amount": "145000.00",
            "payer_inn": "1234567890",
            "document_number": "PAY-328",
            "document_date": "2024-04-27T21:00:00Z"
        }

    def test_process_valid_webhook(self):
        response = self.client.post(
            self.webhook_url,
            data=self.sample_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check organization created with correct balance
        org = Organization.objects.get(inn=self.sample_data['payer_inn'])
        self.assertEqual(org.balance, float(self.sample_data['amount']))
        
        # Check payment created
        self.assertTrue(Payment.objects.filter(
            operation_id=self.sample_data['operation_id']
        ).exists())

    def test_duplicate_webhook(self):
        # First request
        self.client.post(self.webhook_url, data=self.sample_data, format='json')
        
        # Second request with same operation_id
        response = self.client.post(
            self.webhook_url,
            data=self.sample_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should be only one payment and no balance change
        org = Organization.objects.get(inn=self.sample_data['payer_inn'])
        self.assertEqual(org.balance, float(self.sample_data['amount']))
        self.assertEqual(Payment.objects.count(), 1)

    def test_invalid_data(self):
        invalid_data = self.sample_data.copy()
        invalid_data['amount'] = "-100.00"
        
        response = self.client.post(
            self.webhook_url,
            data=invalid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class OrganizationBalanceTests(TestCase):
    """Тесты для получения баланса организации."""
    def setUp(self):
        self.client = APIClient()
        self.org = Organization.objects.create(inn="1234567890", balance=1000)
        self.url = reverse('organization-balance', kwargs={'inn': self.org.inn})

    def test_get_balance(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Сравниваем как строки или преобразуем к float
        self.assertEqual(float(response.data['balance']), float(self.org.balance))

    def test_nonexistent_organization(self):
        response = self.client.get(
            reverse('organization-balance', kwargs={'inn': '0000000000'})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)