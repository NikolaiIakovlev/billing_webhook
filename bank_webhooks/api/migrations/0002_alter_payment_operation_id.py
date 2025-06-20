# Generated by Django 4.2.17 on 2025-06-14 18:38

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='operation_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier of the payment operation', unique=True, verbose_name='Operation ID'),
        ),
    ]
