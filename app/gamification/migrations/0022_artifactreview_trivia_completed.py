# Generated by Django 3.2 on 2023-06-03 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0021_auto_20230602_1646'),
    ]

    operations = [
        migrations.AddField(
            model_name='artifactreview',
            name='trivia_completed',
            field=models.BooleanField(default=False),
        ),
    ]
