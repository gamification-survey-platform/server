# Generated by Django 3.2 on 2023-05-04 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0009_auto_20230503_0918'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reward',
            name='exp_point',
        ),
        migrations.RemoveField(
            model_name='reward',
            name='theme',
        ),
        migrations.AddField(
            model_name='reward',
            name='points',
            field=models.IntegerField(default=0, null=True, verbose_name='points'),
        ),
    ]