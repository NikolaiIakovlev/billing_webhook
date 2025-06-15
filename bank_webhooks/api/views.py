from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Organization, Payment, BalanceLog
from .serializers import WebhookSerializer, OrganizationBalanceSerializer
import logging

# Инициализация логгера для этого модуля
logger = logging.getLogger(__name__)


class BankWebhookView(APIView):
    """
    API-эндпоинт для обработки вебхуков от банка о совершенных платежах.
    Обновляет баланс организации на основе полученных данных о платеже.
    """
    def post(self, request):
        # Валидация входящих данных с помощью сериализатора
        serializer = WebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        operation_id = data['operation_id']  # ID операции из банка
        amount = data['amount']              # Сумма платежа
        payer_inn = data['payer_inn']        # ИНН плательщика

        # Проверка на дубликат платежа (по operation_id)
        if Payment.objects.filter(operation_id=operation_id).exists():
            logger.info(f"Duplicate payment with operation_id: {operation_id}")
            return Response(status=status.HTTP_200_OK)

        # Получаем организацию по ИНН или создаем новую с нулевым балансом
        organization, created = Organization.objects.get_or_create(
            inn=payer_inn,
            defaults={'balance': 0}
        )

        # Создаем запись о платеже в базе данных
        payment = Payment.objects.create(**data)

        # Обновляем баланс организации (увеличиваем на сумму платежа)
        organization.balance += amount
        organization.save()

        # Логируем изменение баланса в отдельной таблице истории
        BalanceLog.objects.create(
            organization=organization,
            amount=amount,
            operation_type='deposit',  # Тип операции - пополнение
            payment=payment             # Связь с платежом
        )

        # Записываем в лог информацию об успешной обработке
        logger.info(
            f"Processed payment {operation_id}. "
            f"New balance for {payer_inn}: {organization.balance}"
        )

        # Возвращаем успешный статус (без данных)
        return Response(status=status.HTTP_200_OK)


class OrganizationBalanceView(APIView):
    """
    API-эндпоинт для получения текущего баланса организации по её ИНН.
    """
    def get(self, request, inn):
        # Получаем организацию по ИНН или возвращаем 404
        organization = get_object_or_404(Organization, inn=inn)
        
        # Сериализуем данные организации (только ИНН и баланс)
        serializer = OrganizationBalanceSerializer(organization)
        
        # Возвращаем данные организации
        return Response(serializer.data)