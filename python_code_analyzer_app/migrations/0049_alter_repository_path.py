# Generated by Django 4.0.3 on 2022-05-07 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0048_alter_repository_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='path',
            field=models.CharField(default='C:/tesis/git/5159f86eca8a4c708c9f39b3b8979296', max_length=256),
        ),
    ]
