# Generated by Django 4.0.3 on 2022-03-26 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0016_alter_repository_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='path',
            field=models.CharField(default='C:/tesis/git/418e4d6ffbe043eb9cccce14d816d2d0', max_length=256),
        ),
    ]
