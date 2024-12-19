# Generated by Django 5.1.3 on 2024-12-14 10:49

import django.db.models.deletion
import shortuuid.main
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_home', '0017_alter_lobby_lobby_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='lobby',
            name='lobby_id',
            field=models.CharField(default=shortuuid.main.ShortUUID.uuid, max_length=128, unique=True),
        ),
        migrations.CreateModel(
            name='LobbyMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.CharField(max_length=300)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('lobby', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lobby_messages', to='a_home.lobby')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
    ]
