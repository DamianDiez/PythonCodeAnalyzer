# Generated by Django 4.0.3 on 2022-04-11 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0041_alter_repository_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='path',
            field=models.CharField(default='C:/tesis/git/94ee3edaecea4b29ba5724693f5bcf4f', max_length=256),
        ),
    ]
