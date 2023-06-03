# Generated by Django 3.2 on 2023-06-02 23:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0020_auto_20230531_0942'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedbacksurvey',
            name='trivia',
        ),
        migrations.AddField(
            model_name='surveytemplate',
            name='trivia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gamification.trivia'),
        ),
    ]
