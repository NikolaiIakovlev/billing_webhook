from django.urls import path
from .views import BankWebhookView, OrganizationBalanceView

# Определение URL-маршрутов (endpoints) API
urlpatterns = [
    # Эндпоинт для обработки вебхуков от банка
    # Доступен по URL: /webhook/bank/
    # Использует BankWebhookView для обработки POST-запросов
    path('webhook/bank/', BankWebhookView.as_view(), name='bank-webhook'),
    
    # Эндпоинт для получения баланса организации
    # Доступен по URL: /organizations/<ИНН>/balance/
    # <str:inn> - динамическая часть URL, содержащая ИНН организации
    # Использует OrganizationBalanceView для обработки GET-запросов
    path('organizations/<str:inn>/balance/',
         OrganizationBalanceView.as_view(),
         name='organization-balance'),
         ]