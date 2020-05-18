from django.contrib.auth.models import Group
from django.db import models, migrations


def apply_migration(apps, schema_editor):
    Group.objects.bulk_create([
        Group(name='coacha_admin'),
        Group(name='admin'),
        Group(name='user'),
    ])

def revert_migration(apps, schema_editor):
    Group.objects.filter(
        name__in=[
            'coacha_admin',
            'admin',
            'user',
        ]
    ).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(apply_migration, revert_migration),
        migrations.RemoveField(
            model_name='user',
            name='last_activity',
        ),
    ]
