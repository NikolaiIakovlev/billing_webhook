
from django.contrib import admin
from django.utils.html import format_html
from .models import Organization, Payment, BalanceLog

# Общий CSS стиль для админки
admin.site.site_header = "Администрирование платежной системы"
admin.site.index_title = "Управление данными"
admin.site.site_title = "Админ-панель"

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('inn', 'balance_display', 'created_at', 'updated_at')
    search_fields = ('inn',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('inn', 'balance'),
            'classes': ('wide', 'extrapretty'),
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def balance_display(self, obj):
        color = "green" if obj.balance >= 0 else "red"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ₽</span>', 
            color, 
            format(obj.balance, '.2f')  # Форматируем число отдельно
        )
    balance_display.short_description = 'Баланс'
    
    class Media:
        css = {
            'all': ('css/admin/admin.css',)
        }

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('operation_id_short', 'amount_display', 'payer_inn', 'document_date', 'created_at')
    search_fields = ('operation_id', 'payer_inn', 'document_number')
    list_filter = ('document_date', 'created_at')
    readonly_fields = ('created_at', 'operation_id')
    date_hierarchy = 'document_date'
    
    fieldsets = (
        ('Детали платежа', {
            'fields': ('operation_id', 'amount', 'payer_inn'),
            'classes': ('wide',),
        }),
        ('Документ', {
            'fields': ('document_number', 'document_date'),
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    
    def operation_id_short(self, obj):
        return str(obj.operation_id)[:8] + "..."
    operation_id_short.short_description = 'ID операции'
    
    def amount_display(self, obj):
        return format_html(
            '<span style="font-weight: bold;">{} ₽</span>', 
            format(obj.amount, '.2f')  # Форматируем число отдельно
        )
    amount_display.short_description = 'Сумма'
    
    class Media:
        css = {
            'all': ('css/admin/admin.css',)
        }

@admin.register(BalanceLog)
class BalanceLogAdmin(admin.ModelAdmin):
    list_display = ('organization', 'operation_type_display', 'amount_display', 'created_at')
    list_filter = ('operation_type', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('organization__inn', 'payment__operation_id')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основные данные', {
            'fields': ('organization', 'amount', 'operation_type'),
            'classes': ('wide',),
        }),
        ('Связанные данные', {
            'fields': ('payment', 'metadata'),
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    
    def operation_type_display(self, obj):
        colors = {
            'deposit': 'green',
            'withdrawal': 'red',
            'correction': 'blue'
        }
        color = colors.get(obj.operation_type, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_operation_type_display()
        )
    operation_type_display.short_description = 'Тип операции'
    
    def amount_display(self, obj):
        color = "green" if obj.operation_type == 'deposit' else "red"
        prefix = "+" if obj.operation_type == 'deposit' else "-"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}{} ₽</span>',
            color,
            prefix,
            format(obj.amount, '.2f')  # Форматируем число отдельно
        )
    amount_display.short_description = 'Сумма'
    
    class Media:
        css = {
            'all': ('css/admin/admin.css',)
        }