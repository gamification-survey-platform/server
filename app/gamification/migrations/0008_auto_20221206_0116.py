# Generated by Django 3.2 on 2022-12-06 09:16

import app.gamification.models.course
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0007_artifactreview_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Constraint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.TextField(blank=True, verbose_name='url')),
                ('threshold', models.IntegerField()),
            ],
            options={
                'verbose_name': 'constraint',
                'verbose_name_plural': 'constraints',
                'db_table': 'constraints',
            },
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, verbose_name='description')),
            ],
            options={
                'verbose_name': 'reward',
                'verbose_name_plural': 'rewards',
                'db_table': 'rewards',
            },
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default', models.BooleanField(default=False)),
                ('name', models.CharField(blank=True, max_length=150, verbose_name='Rule name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
            ],
            options={
                'verbose_name': 'rule',
                'verbose_name_plural': 'rules',
                'db_table': 'rules',
            },
        ),
        migrations.AddField(
            model_name='course',
            name='picture',
            field=models.ImageField(blank=True, upload_to='profile_pics', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg']), app.gamification.models.course.FileSizeValidator(max_size=5242880)], verbose_name='course picture'),
        ),
        migrations.AddField(
            model_name='question',
            name='number_of_scale',
            field=models.IntegerField(blank=True, default=5, null=True),
        ),
        migrations.AlterField(
            model_name='artifact',
            name='file',
            field=models.FileField(blank=True, help_text='Upload a PDF file.', upload_to='assignment_files', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])], verbose_name='assignment file'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='date_due',
            field=models.DateTimeField(blank=True, null=True, verbose_name='date due'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='date_released',
            field=models.DateTimeField(blank=True, null=True, verbose_name='date released'),
        ),
        migrations.AlterField(
            model_name='course',
            name='course_number',
            field=models.CharField(blank=True, max_length=150, verbose_name='course number'),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.TextField(choices=[('MULTIPLETEXT', 'Multipletext'), ('FIXEDTEXT', 'Fixedtext'), ('MULTIPLECHOICE', 'Multiplechoice'), ('SLIDEREVIEW', 'Slidereview'), ('TEXTAREA', 'Textarea'), ('NUMBER', 'Number'), ('SCALEMULTIPLECHOICE', 'Scalemultiplechoice')], default='MULTIPLECHOICE'),
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('constraint_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gamification.constraint')),
            ],
            options={
                'verbose_name': 'action',
                'verbose_name_plural': 'actions',
                'db_table': 'actions',
            },
            bases=('gamification.constraint',),
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('constraint_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gamification.constraint')),
            ],
            options={
                'verbose_name': 'point',
                'verbose_name_plural': 'points',
                'db_table': 'points',
            },
            bases=('gamification.constraint',),
        ),
        migrations.CreateModel(
            name='UserReward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reward', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamification.reward')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user reward',
                'verbose_name_plural': 'user rewards',
                'db_table': 'user_reward',
            },
        ),
        migrations.CreateModel(
            name='RuleConstraint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('constraint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamification.constraint')),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamification.rule')),
            ],
            options={
                'verbose_name': 'rule constraint',
                'verbose_name_plural': 'rule constraints',
                'db_table': 'rule_constraints',
            },
        ),
        migrations.AddField(
            model_name='reward',
            name='rule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamification.rule'),
        ),
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('met', models.BooleanField(default=False)),
                ('cur_point', models.FloatField(blank=True, null=True)),
                ('constraint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamification.constraint')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'progress',
                'verbose_name_plural': 'progresses',
                'db_table': 'progresses',
            },
        ),
        migrations.CreateModel(
            name='CourseRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamification.course')),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamification.rule')),
            ],
            options={
                'verbose_name': 'course rule',
                'verbose_name_plural': 'course_rules',
                'db_table': 'course_rules',
            },
        ),
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamification.rule')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamification.registration')),
            ],
            options={
                'verbose_name': 'achievement',
                'verbose_name_plural': 'achievements',
                'db_table': 'achievements',
            },
        ),
    ]
