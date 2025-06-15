from django.contrib import admin

from api.models import Organization, Payment, BalanceLog

admin.site.register(Organization)
admin.site.register(Payment)
admin.site.register(BalanceLog)