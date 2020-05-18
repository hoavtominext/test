from django.contrib.auth.models import Group
from Users.models import User
from django.db import models, migrations


def set_relationship(apps, schema_editor):
    coacha_admin = Group.objects.first()
    for user in User.objects.all():
        if user.is_superuser:
            user.groups.add(coacha_admin)



class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0002_create_user_group'),
    ]

    operations = [
        migrations.RunPython(set_relationship, migrations.RunPython.noop)
    ]
