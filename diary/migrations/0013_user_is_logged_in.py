# Generated by Django 2.1 on 2018-08-21 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0012_remove_user_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_logged_in',
            field=models.BooleanField(default=False),
        ),
    ]
