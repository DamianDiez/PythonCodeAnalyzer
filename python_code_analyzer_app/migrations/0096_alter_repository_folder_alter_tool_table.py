# Generated by Django 4.0.3 on 2023-05-19 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0095_alter_analysistool_tool_alter_repository_folder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='folder',
            field=models.CharField(default='20230519184428957587', max_length=256),
        ),
        migrations.AlterModelTable(
            name='tool',
            table='tool',
        ),
    ]