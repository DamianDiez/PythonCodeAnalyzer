# Generated by Django 4.0.3 on 2022-04-05 01:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0031_alter_repository_path_delete_pylinttool'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='path',
            field=models.CharField(default='C:/tesis/git/11593c1003244cce8054aaf5ce894b35', max_length=256),
        ),
    ]
