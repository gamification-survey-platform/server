# Generated by Django 3.2 on 2023-05-30 20:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0018_theme_multiple_choice'),
    ]

    operations = [
        migrations.AddField(
            model_name='userreward',
            name='date_purchased',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='date purchased'),
        ),
    ]
