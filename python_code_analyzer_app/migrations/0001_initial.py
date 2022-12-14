# Generated by Django 4.0.3 on 2022-03-16 23:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Analysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=15)),
                ('result', models.CharField(max_length=256)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_finished', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'analyzes',
            },
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=256)),
                ('path', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=256)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'repositories',
            },
        ),
        migrations.CreateModel(
            name='Tool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameters', models.CharField(max_length=256)),
                ('name', models.CharField(choices=[('Pylint', 'pylint')], default='Pylint', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='AnalysisTool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_parameters', models.BooleanField(default=True)),
                ('parameters', models.CharField(default=None, max_length=256)),
                ('status', models.CharField(default='Pending', max_length=15)),
                ('result', models.CharField(default='none', max_length=256)),
                ('analysis_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='python_code_analyzer_app.analysis')),
                ('tool_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='python_code_analyzer_app.tool')),
            ],
        ),
        migrations.AddField(
            model_name='analysis',
            name='repository',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='python_code_analyzer_app.repository'),
        ),
    ]
