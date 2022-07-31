# Generated by Django 4.0.3 on 2022-04-11 20:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('python_code_analyzer_app', '0039_analysis_task_id_alter_analysis_date_finished_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='path',
            field=models.CharField(default='C:/tesis/git/50ae17f25d5741d69976cec214ac0f5f', max_length=256),
        ),
        migrations.CreateModel(
            name='CeleryTaskSignal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signal', models.CharField(choices=[('cancel_task', 'Cancel Task'), ('pause_task', 'Pause Task')], max_length=25, null=True)),
                ('completed', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='python_code_analyzer_app.analysis')),
            ],
            options={
                'ordering': ('modified_on',),
            },
        ),
    ]
