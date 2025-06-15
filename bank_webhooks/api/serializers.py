from rest_framework import serializers
from .models import Organization
from django.core.validators import MinLengthValidator


class WebhookSerializer(serializers.Serializer):
    """
    Сериализатор для обработки данных вебхука о платежах.
    Проверяет и валидирует входящие данные о платежах.
    """
    operation_id = serializers.UUIDField()  # Уникальный идентификатор операции
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)  # Сумма платежа
    payer_inn = serializers.CharField(
        max_length=12,
        validators=[MinLengthValidator(10)]  # ИНН плательщика (10-12 символов)
    )
    document_number = serializers.CharField(max_length=50)  # Номер платежного документа
    document_date = serializers.DateTimeField()  # Дата платежного документа

    def validate_amount(self, value):
        """
        Проверка, что сумма платежа положительная.
        
        Args:
            value: Проверяемое значение суммы
            
        Returns:
            value: Валидное значение суммы
            
        Raises:
            ValidationError: Если сумма меньше или равна нулю
        """
        if value <= 0:
            raise serializers.ValidationError("Сумма платежа должна быть больше нуля")
        return value


class OrganizationBalanceSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения баланса организации.
    """
    balance = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False
    )
    
    class Meta:
        model = Organization
        fields = ['inn', 'balance']