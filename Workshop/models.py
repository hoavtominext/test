from django.db import models
from Company.models import Company
from Users.models import User


# Create your models here.
class Workshop(models.Model):
    code = models.CharField(max_length=255,null=False,default='')
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date_workshop = models.DateField()
    remark = models.TextField(blank=True)
    total_user_join = models.IntegerField(null=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workshop"


class UserWorkshop(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE)
    company = models.ForeignKey(Company,on_delete=models.CASCADE,default=1)
    completed_assessment = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_workshop"
