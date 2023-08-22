# Generated by Django 3.2 on 2023-07-12 17:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0029_remove_registration_userrole'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artifactreview',
            name='status',
            field=models.TextField(choices=[('COMPLETED', 'Completed'), ('INCOMPLETE', 'Incomplete'), ('REOPEN', 'Reopen')], default='INCOMPLETE'),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.TextField(blank=True, choices=[('MESSAGE', 'Message'), ('POKE', 'Poke')], default='POKE')),
                ('text', models.TextField(blank=True, verbose_name='text')),
                ('is_read', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'notification',
                'verbose_name_plural': 'notifications',
                'db_table': 'notifications',
            },
        ),
    ]