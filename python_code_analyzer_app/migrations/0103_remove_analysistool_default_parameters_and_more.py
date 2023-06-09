# Generated by Django 4.0.3 on 2023-06-09 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0102_remove_tool_parameters_alter_repository_folder'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analysistool',
            name='default_parameters',
        ),
        migrations.RemoveField(
            model_name='analysistool',
            name='parameters',
        ),
        migrations.AlterField(
            model_name='repository',
            name='folder',
            field=models.CharField(default='20230609091025891443', max_length=256),
        ),
    ]
