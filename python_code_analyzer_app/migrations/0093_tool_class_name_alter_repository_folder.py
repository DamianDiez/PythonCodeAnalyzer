# Generated by Django 4.0.3 on 2022-10-07 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0092_analysis_commit_analysis_status_msg_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tool',
            name='class_name',
            field=models.CharField(default='', max_length=256),
        ),
        migrations.AlterField(
            model_name='repository',
            name='folder',
            field=models.CharField(default='20221007183603855184', max_length=256),
        ),
    ]