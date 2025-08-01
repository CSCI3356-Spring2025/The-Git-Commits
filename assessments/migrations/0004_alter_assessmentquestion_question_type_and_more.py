# Generated by Django 5.1.6 on 2025-04-14 05:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0003_alter_assessmentquestion_question_type_and_more'),
        ('oauth', '0010_remove_user_course_remove_user_team_user_courses_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessmentquestion',
            name='question_type',
            field=models.CharField(choices=[('likert', 'Likert'), ('free', 'Free Response')], max_length=20),
        ),
        migrations.AlterField(
            model_name='studentassessmentresponse',
            name='evaluated_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='evaluations_received', to='oauth.user'),
        ),
        migrations.AlterField(
            model_name='studentassessmentresponse',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oauth.user'),
        ),
    ]
