# Generated by Django 4.0.3 on 2022-04-01 20:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0028_alter_repository_path'),
    ]

    operations = [
        migrations.CreateModel(
            name='PylintTool',
            fields=[
                ('tool_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='python_code_analyzer_app.tool')),
            ],
            bases=('python_code_analyzer_app.tool',),
        ),
        migrations.AlterField(
            model_name='repository',
            name='path',
            field=models.CharField(default='C:/tesis/git/758770eb5edb45d89a7a34e0ce9fa8ee', max_length=256),
        ),
    ]
