# Generated by Django 2.1 on 2018-08-13 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0006_auto_20180813_1756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='token',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]