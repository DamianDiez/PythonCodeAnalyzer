# Generated by Django 4.0.3 on 2022-09-24 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0091_repository_owner_alter_repository_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='commit',
            field=models.CharField(default='null', max_length=40),
        ),
        migrations.AddField(
            model_name='analysis',
            name='status_msg',
            field=models.CharField(default='null', max_length=256),
        ),
        migrations.AlterField(
            model_name='repository',
            name='folder',
            field=models.CharField(default='20220924105747025209', max_length=256),
        ),
    ]
