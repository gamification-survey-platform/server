# Generated by Django 3.2 on 2023-05-25 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0015_auto_20230519_1933'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='gamified',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='question',
            name='phrased_positively',
            field=models.BooleanField(default=True),
        ),
    ]
