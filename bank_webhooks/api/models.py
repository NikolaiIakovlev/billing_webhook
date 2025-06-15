from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _  # Для поддержки перевода строк
from django.core.validators import RegexValidator  # Для валидации по регулярным выражениям
import uuid



class Organization(models.Model):
    """
    Модель организации с основными реквизитами.
    Хранит ИНН и текущий баланс организации.
    """
    
    class Meta:
        # Настройки метаданных модели:
        verbose_name = _("Organization")  # Человекочитаемое имя в единственном числе
        verbose_name_plural = _("Organizations")  # Во множественном числе
        ordering = ['inn']  # Сортировка по умолчанию
        indexes = [
            # Индекс для ускорения поиска по ИНН
            models.Index(fields=['inn']),
        ]

    # ИНН организации - основной идентификатор
    inn = models.CharField(
        _("INN"),  # Локализованное название поля
        max_length=12,  # Максимальная длина (10 или 12 цифр)
        validators=[
            MinLengthValidator(10),  # Минимальная длина 10 символов
            RegexValidator(
                regex='^[0-9]*$',  # Только цифры
                message=_("INN must contain only digits")  # Сообщение об ошибке
            )
        ],
        unique=True,  # Уникальное значение
        primary_key=True,  # Используем как первичный ключ
        help_text=_("Taxpayer Identification Number (10 or 12 digits)")  # Подсказка для админки
    )
    
    # Текущий баланс организации
    balance = models.DecimalField(
        _("Balance"),
        max_digits=15,  # Максимум 15 цифр всего
        decimal_places=2,  # 2 знака после запятой
        default=0,  # Начальный баланс
        validators=[MinValueValidator(0)],  # Не может быть отрицательным
        help_text=_("Current organization balance in currency units")
    )

    # Автоматически добавляемая дата создания
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,  # Устанавливается при создании
        db_index=True  # Индекс для ускорения фильтрации
    )
    
    # Автоматически обновляемая дата изменения
    updated_at = models.DateTimeField(
        _("Updated at"),
        auto_now=True  # Обновляется при каждом сохранении
    )

    def __str__(self):
        """Строковое представление объекта для админки и отладочных сообщений"""
        return _("Organization %(inn)s") % {'inn': self.inn}


class Payment(models.Model):
    """
    Модель платежа с деталями транзакции.
    Хранит информацию о входящих платежах от банка.
    """
    
    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ['-document_date']  # Сортировка по дате документа (новые сначала)
        indexes = [
            # Индексы для часто фильтруемых полей
            models.Index(fields=['operation_id']),
            models.Index(fields=['payer_inn']),
            models.Index(fields=['document_date']),
        ]
        constraints = [
            # Гарантируем уникальность operation_id на уровне БД
            models.UniqueConstraint(
                fields=['operation_id'],
                name='unique_operation_id'
            ),
        ]

    # Уникальный идентификатор операции (UUID)
    operation_id = models.UUIDField(
        _("Operation ID"),
        unique=True,
        editable=False,
        default=uuid.uuid4,  # ← Вот это ключевое изменение
        help_text=_("Unique identifier of the payment operation")
    )
    
    # Сумма платежа
    amount = models.DecimalField(
        _("Amount"),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],  # Минимальная сумма 0.01
        help_text=_("Payment amount in currency units")
    )
    
    # ИНН плательщика
    payer_inn = models.CharField(
        _("Payer INN"),
        max_length=12,
        validators=[MinLengthValidator(10)],  # Минимум 10 символов
        help_text=_("Taxpayer Identification Number of the payer")
    )
    
    # Номер платежного документа
    document_number = models.CharField(
        _("Document number"),
        max_length=50,  # Достаточно для большинства номеров документов
        help_text=_("Payment document reference number")
    )
    
    # Дата документа
    document_date = models.DateTimeField(
        _("Document date"),
        help_text=_("Date and time when payment document was issued")
    )
    
    # Дата создания записи
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,  # Устанавливается один раз при создании
        db_index=True  # Индекс для быстрого поиска новых платежей
    )

    def __str__(self):
        """Строковое представление для отладки"""
        return _("Payment %(operation_id)s") % {'operation_id': self.operation_id}


class BalanceLog(models.Model):
    """
    Лог изменений баланса организации.
    Фиксирует все операции по изменению баланса.
    """
    
    # Типы операций с балансом
    class OperationType(models.TextChoices):
        DEPOSIT = 'deposit', _("Deposit")  # Пополнение
        WITHDRAWAL = 'withdrawal', _("Withdrawal")  # Списание
        CORRECTION = 'correction', _("Correction")  # Корректировка

    class Meta:
        verbose_name = _("Balance Log")
        verbose_name_plural = _("Balance Logs")
        ordering = ['-created_at']  # Новые записи сначала
        indexes = [
            # Индексы для часто используемых фильтров
            models.Index(fields=['organization']),
            models.Index(fields=['created_at']),
            models.Index(fields=['operation_type']),
        ]

    # Ссылка на организацию
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,  # При удалении организации удаляем логи
        related_name='balance_logs',  # Имя для обратной связи
        verbose_name=_("Organization")
    )
    
    # Сумма изменения баланса
    amount = models.DecimalField(
        _("Amount"),
        max_digits=15,
        decimal_places=2,
        help_text=_("Amount of balance change")
    )
    
    # Тип операции
    operation_type = models.CharField(
        _("Operation type"),
        max_length=10,
        choices=OperationType.choices,  # Выбор из предопределенных значений
        default=OperationType.DEPOSIT,
        help_text=_("Type of balance operation")
    )
    
    # Ссылка на платеж (если есть)
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,  # При удалении платежа оставляем запись
        null=True,  # Может быть NULL
        blank=True,  # Может быть пустым в формах
        related_name='balance_logs',
        verbose_name=_("Payment")
    )
    
    # Дата создания записи
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,  # Устанавливается при создании
        db_index=True  # Индекс для быстрого поиска
    )
    
    # Дополнительные метаданные операции
    metadata = models.JSONField(
        _("Metadata"),
        default=dict,  # По умолчанию пустой словарь
        blank=True,  # Может быть пустым
        help_text=_("Additional operation context data")
    )

    def __str__(self):
        """Человекочитаемое представление записи"""
        return _("%(operation_type)s %(amount)s for %(inn)s") % {
                    'operation_type': self.OperationType(self.operation_type).label,  # Используем .label
                    'amount': self.amount,
                    'inn': self.organization.inn
                }