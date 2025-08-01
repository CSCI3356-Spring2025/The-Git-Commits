# Generated by Django 5.1.6 on 2025-04-12 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0008_remove_assessmentquestion_assessment_and_more'),
        ('oauth', '0009_merge_20250330_1628'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='course',
        ),
        migrations.RemoveField(
            model_name='user',
            name='team',
        ),
        migrations.AddField(
            model_name='user',
            name='courses',
            field=models.ManyToManyField(blank=True, related_name='members', to='landing.course'),
        ),
        migrations.AddField(
            model_name='user',
            name='teams',
            field=models.ManyToManyField(blank=True, related_name='members', to='landing.team'),
        ),
    ]
