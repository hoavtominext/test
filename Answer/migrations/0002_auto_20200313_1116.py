# Generated by Django 2.2.6 on 2020-03-13 11:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Answer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='workshop',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='Workshop', to='Workshop.Workshop'),
        ),
        migrations.AlterField(
            model_name='result',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Company.Company'),
        ),
    ]
