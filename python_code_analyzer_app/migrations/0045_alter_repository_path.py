# Generated by Django 4.0.3 on 2022-05-07 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0044_alter_repository_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='path',
            field=models.CharField(default='C:/tesis/git/8ede4c3d40664d61862a40eab1bfc84e', max_length=256),
        ),
    ]
