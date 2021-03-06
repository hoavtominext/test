# Generated by Django 2.2.6 on 2020-03-04 09:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Company', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Workshop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('date_workshop', models.DateField()),
                ('total_user_join', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Company.Company')),
            ],
            options={
                'db_table': 'workshop',
            },
        ),
        migrations.CreateModel(
            name='UserWorkshop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed_assessment', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Company.Company')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('workshop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Workshop.Workshop')),
            ],
            options={
                'db_table': 'user_workshop',
            },
        ),
    ]
