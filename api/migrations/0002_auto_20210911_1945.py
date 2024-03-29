# Generated by Django 2.2.19 on 2021-09-11 14:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ElementInVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'элемент в версии справочника',
                'verbose_name_plural': 'элементы в версии справочника',
            },
        ),
        migrations.RemoveConstraint(
            model_name='element',
            name='unique_elements_code_value',
        ),
        migrations.RemoveField(
            model_name='element',
            name='version',
        ),
        migrations.AlterField(
            model_name='element',
            name='code',
            field=models.CharField(db_index=True, max_length=50, verbose_name='код'),
        ),
        migrations.AlterField(
            model_name='element',
            name='value',
            field=models.CharField(max_length=100, verbose_name='значение'),
        ),
        migrations.AlterField(
            model_name='guide',
            name='short_title',
            field=models.CharField(max_length=50, unique=True, verbose_name='короткое наименование'),
        ),
        migrations.AddConstraint(
            model_name='element',
            constraint=models.UniqueConstraint(fields=('code', 'value'), name='unique_code_value'),
        ),
        migrations.AddField(
            model_name='elementinversion',
            name='element',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Element', verbose_name='элемент'),
        ),
        migrations.AddField(
            model_name='elementinversion',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='version_elements', to='api.Version', verbose_name='версия'),
        ),
        migrations.AddField(
            model_name='version',
            name='elements',
            field=models.ManyToManyField(through='api.ElementInVersion', to='api.Element', verbose_name='элемент в версии'),
        ),
    ]
