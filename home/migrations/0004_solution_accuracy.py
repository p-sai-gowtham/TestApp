# Generated by Django 5.0.3 on 2024-03-22 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_solution_teacher_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='accuracy',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
