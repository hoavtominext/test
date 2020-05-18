import datetime

from django.db import models

from django.contrib.auth.models import User
from datetime import datetime
from Company.models import Company
from Department.models import Department
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other')
)

from django.contrib.auth.models import AbstractUser

class UserMixinIsUserAdmin(models.Model):
    cronjob_mail_magazine = models.CharField(default='',max_length=50)

    class Meta:
        abstract = True

# Only for LAST_ACTIVITY = True
class User(AbstractUser,UserMixinIsUserAdmin):
    pass

    class Meta:
        db_table = "users"

    def getCronjobMailMagazine(self):
        cronjob_mail_magazine = self.cronjob_mail_magazine
        if cronjob_mail_magazine is None or cronjob_mail_magazine is '':
            return False
        else:
            day_weeks = cronjob_mail_magazine.split(',')
            return day_weeks

class UserProfile(models.Model):
    LOCK_CHOICES = (
        ('LOCKED', "Account Locked"),
        ('UNLOCKED', "Account Unlocked")
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='user_company', default=1)
    department = models.CharField(max_length=255, null=True,blank=True)
    employee_id = models.CharField(max_length=255, null=True)
    first_furigana = models.CharField(max_length=255, null=True)
    last_furigana = models.CharField(max_length=255, null=True)
    language = models.CharField(max_length=255, null=True)
    birthday = models.DateField(null=True, blank=True)
    sex = models.BooleanField(default=None, null=True)
    position_department = models.CharField(max_length=255, null=True)
    company_date_joined = models.DateField(null=True,blank=True)
    authority = models.CharField(max_length=255, null=True)
    is_send_email = models.BooleanField(default=False)
    no_login_attempt = models.IntegerField(default=0)
    lock_status = models.CharField( max_length=10, choices=LOCK_CHOICES, default="UNLOCKED")

    class Meta:
        db_table = "profile"
        unique_together = ('user',)
