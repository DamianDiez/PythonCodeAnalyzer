# Generated by Django 4.0.3 on 2022-03-16 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='herramientas',
            field=models.ManyToManyField(through='python_code_analyzer_app.AnalysisTool', to='python_code_analyzer_app.tool'),
        ),
    ]
