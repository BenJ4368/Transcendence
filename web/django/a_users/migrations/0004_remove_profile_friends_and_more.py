# Generated by Django 5.1.3 on 2024-11-28 12:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('a_users', '0003_profile_friends_profile_pending_request'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='friends',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='pending_request',
        ),
    ]
