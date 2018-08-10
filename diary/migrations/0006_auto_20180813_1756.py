# Generated by Django 2.1 on 2018-08-13 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0005_auto_20180813_1709'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blacklisttoken',
            name='owner',
        ),
        migrations.AddField(
            model_name='user',
            name='token',
            field=models.CharField(blank=True, default=None, max_length=128, null=True),
        ),
        migrations.DeleteModel(
            name='BlackListToken',
        ),
    ]