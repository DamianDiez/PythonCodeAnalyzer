# Generated by Django 4.0.3 on 2022-06-06 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0086_alter_repository_folder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='folder',
            field=models.CharField(default='20220606171715810370', max_length=256),
        ),
    ]
