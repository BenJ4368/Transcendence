# Generated by Django 5.1.3 on 2024-11-28 12:04

import shortuuid.main
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_home', '0010_alter_lobby_lobby_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lobby',
            name='lobby_id',
            field=models.CharField(default=shortuuid.main.ShortUUID.uuid, max_length=128, unique=True),
        ),
    ]
