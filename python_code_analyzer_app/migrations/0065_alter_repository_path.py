# Generated by Django 4.0.3 on 2022-05-13 02:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0064_alter_repository_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='path',
            field=models.CharField(default='C:/tesis/git/6106f6871a3a4186a0ec07eda20729ae', max_length=256),
        ),
    ]
