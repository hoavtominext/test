# Generated by Django 2.2.6 on 2020-03-24 12:11

import Company.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Company', '0003_auto_20200306_1006'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyIpList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.CharField(max_length=15, validators=[Company.models.ip_validator], verbose_name='IP Address')),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ip_list', to='Company.Company')),
            ],
            options={
                'db_table': 'companyiplist',
                'unique_together': {('company', 'ip_address')},
            },
        ),
    ]
