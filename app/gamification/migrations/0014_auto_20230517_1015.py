# Generated by Django 3.2 on 2023-05-17 17:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0013_auto_20230509_0947'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='question_option',
        ),
        migrations.RemoveField(
            model_name='question',
            name='dependent_question',
        ),
        migrations.RemoveField(
            model_name='question',
            name='is_multiple',
        ),
        migrations.RemoveField(
            model_name='question',
            name='is_template',
        ),
        migrations.RemoveField(
            model_name='question',
            name='option_choices',
        ),
        migrations.AddField(
            model_name='answer',
            name='option_choice',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='gamification.optionchoice'),
        ),
        migrations.AddField(
            model_name='optionchoice',
            name='question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gamification.question'),
        ),
        migrations.AddField(
            model_name='question',
            name='number_of_text',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.TextField(choices=[('MULTIPLETEXT', 'Multipletext'), ('FIXEDTEXT', 'Fixedtext'), ('MULTIPLECHOICE', 'Multiplechoice'), ('SLIDEREVIEW', 'Slidereview'), ('TEXTAREA', 'Textarea'), ('NUMBER', 'Number'), ('SCALEMULTIPLECHOICE', 'Scalemultiplechoice'), ('MULTIPLESELECT', 'Multipleselect')], default='MULTIPLECHOICE'),
        ),
        migrations.AlterField(
            model_name='reward',
            name='reward_type',
            field=models.TextField(choices=[('Other', 'Other'), ('Late Submission', 'Late Submission'), ('Bonus', 'Bonus')], default='Other'),
        ),
        migrations.DeleteModel(
            name='QuestionOption',
        ),
    ]
