# Generated by Django 4.0.3 on 2022-05-13 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0063_alter_repository_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='path',
            field=models.CharField(default='C:/tesis/git/ac4b661b68704714b9595d2110ebee5d', max_length=256),
        ),
    ]
