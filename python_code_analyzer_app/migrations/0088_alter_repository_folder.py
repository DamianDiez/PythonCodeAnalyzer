# Generated by Django 4.0.3 on 2022-06-06 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0087_alter_repository_folder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='folder',
            field=models.CharField(default='20220606172825602672', max_length=256),
        ),
    ]
