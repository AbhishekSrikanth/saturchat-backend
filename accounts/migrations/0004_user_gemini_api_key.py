# Generated by Django 5.1.7 on 2025-04-16 03:39

import encrypted_fields.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_user_anthropic_api_key_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gemini_api_key',
            field=encrypted_fields.fields.EncryptedCharField(blank=True, max_length=255, null=True),
        ),
    ]
